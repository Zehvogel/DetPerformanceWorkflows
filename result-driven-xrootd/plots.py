#!/usr/bin/env python
# coding: utf-8

import ROOT
import numpy as np
from cld_style import cldStyle
import argparse
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--energies", action="store", nargs="+", metavar=("file1", "file2"), help="One or multiple input files", default=[5., 10., 20., 50., 100.])
parser.add_argument("--n_events", action="store", type=int, help="Number of events in the input files", default=1000)
parser.add_argument("--input_path", action="store", type=str, help="Path to the input files", default="ntuples")
parser.add_argument("--output_path", action="store", type=str, help="Path to save the output plots", default="plots")
parser.add_argument("--particle", action="store", type=str, help="Particle type (e.g., gamma, kaon0L)", default="gamma")
parser.add_argument("--n_bins", action="store", type=int, help="Number of bins for the histograms", default=30)
parser.add_argument("--n_threads", action="store", type=int, help="Number of threads to use for parallel processing", default=1)
parser.add_argument("--batch", action="store_true", help="Run in batch mode (no GUI)")
args = parser.parse_args()

# energies = [5., 10., 20., 50., 100.]
energies = [float(e) for e in args.energies]
n_events = args.n_events
plot_path = Path(args.output_path)
plot_path.mkdir(parents=True, exist_ok=True)
input_path = Path(args.input_path)
particle = args.particle

n_threads = args.n_threads
n_bins = args.n_bins

if args.batch:
    ROOT.gROOT.SetBatch(True)

cldStyle.SetOptStat(1)
cldStyle.SetOptFit(1)
cldStyle.cd()

ROOT.gStyle.SetOptFit(1)
ROOT.EnableImplicitMT(n_threads)

dfs = {}
for e in energies:
    df = ROOT.RDataFrame("PFONtuple", str(input_path / f"{particle}_{e}_cosTheta_{n_events}N.root"))
    dfs[e] = df


deg = np.pi / 180
# TODO: should probably be made configurable
regions = {
    "barrel": f"true_theta > {50*deg} && true_theta < {130*deg}",
    "endcap": f"(true_theta > {15*deg} && true_theta < {40*deg}) || (true_theta > {140*deg} && true_theta < {165*deg})",
    "transition": f"(true_theta > {40*deg} && true_theta < {50*deg}) || (true_theta > {130*deg} && true_theta < {140*deg})",
}
legend_map = {
    "barrel": "Barrel (50#circ < #theta < 130#circ)",
    "endcap": "Endcap (15#circ < #theta < 40#circ)",
    "transition": "Transition (40#circ < #theta < 50#circ)",
}

colls = {region: {} for region in regions}
region_dfs = {region: {} for region in regions}
for k, df in dfs.items():
    # only care about the stable particle
    df = df.Filter("mc_genStatus == 1")
    df = df.Filter("has_cluster")
    df = df.Define("true_theta", "std::atan2(std::hypot(mc_Px, mc_Py), mc_Pz)")
    df = df.Define("delta_E", "pfo_E - mc_E")
    for region, region_cut in regions.items():
        region_df = df.Filter(region_cut)
        colls[region][k] = region_df.Take["double"]("delta_E")
        region_dfs[region][k] = region_df
    dfs[k] = df

# tell root that we want to access all these values next so that it can run in parallel
# (useless overkill)
ROOT.RDF.RunGraphs([coll for region_colls in colls.values() for coll in region_colls.values()])

stds = {}
means = {}
counts = {}
for region, region_colls in colls.items():
    stds[region] = {}
    means[region] = {}
    counts[region] = {}
    for k, coll in region_colls.items():
        col = np.asarray(coll.GetValue())
        med = np.median(col)
        mad = np.median(np.abs(col - med))
        # using the median absolute deviation as estimator of the standard deviation
        stds[region][k] = 1.4826 * mad
        means[region][k] = med
        counts[region][k] = len(col)

histos = {}
sigma_E = {}
means_E = {}
for region, region_frames in region_dfs.items():
    histos[region] = {}
    sigma_E[region] = []
    means_E[region] = []
    for k, df in region_frames.items():
        low_bin = means[region][k] - 3 * stds[region][k]
        high_bin = means[region][k] + 3 * stds[region][k]
        bin_width = (high_bin - low_bin) / n_bins
        h = df.Histo1D(("", ";E_{REC} - E_{MC}", n_bins, low_bin, high_bin), "delta_E")

        # f = ROOT.TF1(f"f_delta_E_{k}", "gausn", low_bin, high_bin)
        # instead of gausn, the below returns a useful amplitude while keeping the correlation with the width
        f = ROOT.TF1(f"f_delta_E_{region}_{k}", "[0]*exp(-0.5*((x-[1])/[2])**2/[2])", low_bin, high_bin)

        scale = counts[region][k] * bin_width / (np.sqrt(2* np.pi))

        f.SetParameters(scale, means[region][k], stds[region][k])
        h.Fit(f, "L")
        sigma_E[region].append(f.GetParameter(2))
        means_E[region].append(f.GetParameter(1))

        histos[region][k] = h

# plot individual slices
canvs = {}
for region, region_histos in histos.items():
    canvs[region] = {}
    for k, h in region_histos.items():
        c = ROOT.TCanvas()
        h.Draw()
        c.Draw()
        canvs[region][k] = c

# energy resolution plot
mg_res_E = ROOT.TMultiGraph()
l = ROOT.TLegend(0.7, 0.7, 1., 1.)
for i, (region, region_sigmas) in enumerate(sigma_E.items()):
    energies = np.array(energies, dtype=np.float64)
    resolutions = np.array(region_sigmas, dtype=np.float64) / energies
    g = ROOT.TGraph(len(energies), energies, resolutions)
    g.SetLineColor(ROOT.kP6Blue + i)
    g.SetMarkerColor(ROOT.kP6Blue + i)
    l.AddEntry(g, legend_map[region], "lp")
    mg_res_E.Add(g)

c_res_E = ROOT.TCanvas()
mg_res_E.SetMinimum(0.0)
mg_res_E.Draw("A LP")
mg_res_E.SetTitle(";E_{MC} [GeV];#sigma(E_{REC} - E_{MC}) / E_{MC}")
l.Draw()
c_res_E.Draw()
c_res_E.SaveAs(str(plot_path / "neutral_energy_resolution.pdf"))

# bias plot
mg_bias_E = ROOT.TMultiGraph()
l = ROOT.TLegend(0.7, 0.2, 1., 0.5)
for i, (region, region_means) in enumerate(means_E.items()):
    energies = np.array(energies, dtype=np.float64)
    biases = np.array(region_means, dtype=np.float64) / energies
    g = ROOT.TGraph(len(energies), energies, biases)
    g.SetLineColor(ROOT.kP6Blue + i)
    g.SetMarkerColor(ROOT.kP6Blue + i)
    l.AddEntry(g, legend_map[region], "lp")
    mg_bias_E.Add(g)

c_bias_E = ROOT.TCanvas()
mg_bias_E.Draw("A LP")
mg_bias_E.SetTitle(";E_{MC} [GeV];#mu(E_{REC} - E_{MC}) / E_{MC}")
l.Draw()
c_bias_E.Draw()
