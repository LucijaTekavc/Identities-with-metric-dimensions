
import os
import csv


os.makedirs("./csvs", exist_ok=True)

with open("./csvs/eq_graphs.csv", "w") as csvfile:
    writer = csv.DictWriter(
        csvfile, fieldnames=["vertices", "index", "dimension"]
    )
    writer.writeheader()
    for filename in os.listdir("./eq_graphs/"):
        n, ix, _, dim = filename.split("_")
        dim = dim.removeprefix("d")
        row = dict(vertices=n, index=ix, dimension=dim)
        writer.writerow(row)

with open("./csvs/mdim_graphs.csv", "w") as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=["vertices", "index", "metric_dim",  "edge_dim",  "mixed_dim"]
    )
    writer.writeheader()
    for filename in os.listdir("./mdim_graphs/"):
        n, ix, _, dim, edim = filename.split("_")
        dim, edim = dim.removeprefix("d"), edim.removeprefix("e")
        mdim = dim + edim
        row = dict(vertices=n, index=ix, metric_dim=dim, edge_dim=edim, mixed_dim=mdim)
        writer.writerow(row)
