import ROOT

# largely adapted from the ildStyle .rootlogon.C macro

cldStyle = ROOT.TStyle("cldStyle", "CLD Style");

# set the background color to white
cldStyle.SetFillColor(10)
cldStyle.SetFrameFillColor(10)
cldStyle.SetCanvasColor(10)
cldStyle.SetPadColor(10)
cldStyle.SetTitleFillColor(0)
cldStyle.SetStatColor(10)

# dont put a colored frame around the plots
cldStyle.SetFrameBorderMode(0)
cldStyle.SetCanvasBorderMode(0)
cldStyle.SetPadBorderMode(0)
cldStyle.SetLegendBorderSize(0)

# use the primary color palette
# FIXME: this palette is absolutely horrible!!!
cldStyle.SetPalette(1,0)

# set the default line color for a histogram to be black
cldStyle.SetHistLineColor(ROOT.kBlack)

# set the default line color for a fit function to be red
cldStyle.SetFuncColor(ROOT.kRed)

# make the axis labels black
cldStyle.SetLabelColor(ROOT.kBlack,"xyz")

# set the default title color to be black
cldStyle.SetTitleColor(ROOT.kBlack)

# set the margins
# XXX: in the end these need to be manually tuned for most plots
cldStyle.SetPadBottomMargin(0.17)
cldStyle.SetPadTopMargin(0.08)
cldStyle.SetPadRightMargin(0.16)
cldStyle.SetPadLeftMargin(0.15)

# set axis label and title text sizes
cldStyle.SetLabelFont(42,"xyz")
cldStyle.SetLabelSize(0.06,"xyz")
cldStyle.SetLabelOffset(0.015,"xyz")
cldStyle.SetTitleFont(42,"xyz")
cldStyle.SetTitleSize(0.07,"xyz")
cldStyle.SetTitleOffset(1.1,"yz")
cldStyle.SetTitleOffset(1.0,"x")
cldStyle.SetStatFont(42)
cldStyle.SetStatFontSize(0.06)
cldStyle.SetTitleBorderSize(0)
cldStyle.SetStatBorderSize(0)
cldStyle.SetTextFont(42)

# set line widths
cldStyle.SetFrameLineWidth(2)
cldStyle.SetFuncWidth(2)
cldStyle.SetHistLineWidth(2)

# set the number of divisions to show
cldStyle.SetNdivisions(506, "xy")

# turn off xy grids
cldStyle.SetPadGridX(0)
cldStyle.SetPadGridY(0)

# set the tick mark style
cldStyle.SetPadTickX(1)
cldStyle.SetPadTickY(1)

# turn off stats
# TODO: make this easier to toggle
cldStyle.SetOptStat(0)
cldStyle.SetOptFit(0)

# marker settings
cldStyle.SetMarkerStyle(20)
cldStyle.SetMarkerSize(0.7)
cldStyle.SetLineWidth(2)
