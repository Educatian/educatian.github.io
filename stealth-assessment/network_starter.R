library(igraph)
library(tidygraph)
library(ggraph)

# Tiny example help network for a collaborative learning task.
edges <- data.frame(
  from = c("P01", "P01", "P02", "P03", "P04"),
  to   = c("P02", "P03", "P04", "P04", "P02"),
  weight = c(3, 2, 1, 4, 2)
)

g <- graph_from_data_frame(edges, directed = TRUE)
print(centr_degree(g, mode = "all"))

tbl_g <- as_tbl_graph(g)
ggraph(tbl_g, layout = "fr") +
  geom_edge_link(aes(width = weight), alpha = 0.5) +
  geom_node_point(size = 8, color = "#1E6A57") +
  geom_node_text(aes(label = name), repel = TRUE) +
  theme_void()
