# Data points retrieved from the web service with the following command run on awesome:
# tail -f /var/log/celery/mrocp.log | egrep --line-buffered 'downsampling to factor|Completed building graph in |Your atlas has|took' | tee filtered_output.txt

# This was tested on KKI2009_800_1_bg.graphml

# Variables:
# dsf      <- downsample factor
# n       <- compute node the job ran on (helped trace times from logs)
# read_t  <- time taken to read the graph in from disk
# atlas_t <- time taken to create downsampled atlas
# rois    <- number of nodes in downsampled atlas
# graph_t <- time taken to create downsampled graph

require(ggplot2)
require(reshape2)
require(RColorBrewer)

dsf      <- c(       1,       2,       3,       4,       5,       6,       7,       8,       9,      10,      11,      12,      13,      14,      15,      16,      17,      18,      19,      20)
n       <- c(      37,       9,      62,      10,      10,      53,      57,      16,      41,      18,      56,       8,      34,      54,      36,      55,      36,      38,      31,      15)
read_t  <- c( 340.528, 353.915, 338.184, 333.049, 361.656, 386.632, 342.045, 356.185, 366.633, 363.878, 355.005, 391.875, 365.821, 374.181, 402.091, 363.688, 379.822, 377.135, 367.739, 378.941)
atlas_t <- c(   3.813,   3.105,   3.161,   3.108,   2.953,   2.722,   2.938,   3.536,   2.958,   4.629,   2.713,   3.547,   2.872,   3.209,   2.996,   2.992,   3.506,   2.748,   2.946,   3.802)
rois    <- c(   72784,   16784,    6481,    3231,    1876,    1216,     833,     583,     446,     350,     278,     230,     195,     172,     140,     116,     108,      96,      81,      71)
graph_t <- c( 278.539, 230.834, 244.424, 216.429, 211.208, 225.265, 214.230, 202.506, 203.205, 197.852, 190.036, 228.073, 192.104, 187.261, 181.779, 183.726, 182.287, 201.936, 189.283, 175.146)

labs <- c("Graph Generation", "Graph Read")
df <- data.frame(dsf, graph_t, read_t)
# df <- data.frame(dsf, graph_t, atlas_t, read_t)
# df <- data.frame(dsf, rois, graph_t, atlas_t, read_t)

df2 <- melt(df,  id.vars = 'dsf', variable.name = 'time')
cols <- brewer.pal(3, 'Accent')[2:3]
plt <- ggplot(df2, aes(x = dsf, y = value, color = time, group = time)) + geom_line(size=1.5) + geom_point(size=2) +
       scale_color_manual("Process\n",labels = labs, values = cols) +
       labs(title="Processing Time for Graph Downsampling to Various Factors",x='Downsample Factor', y = "Time (s)") +
       theme(text = element_text(size=20), axis.text.x = element_text(angle=00, vjust=1)) 
plt
