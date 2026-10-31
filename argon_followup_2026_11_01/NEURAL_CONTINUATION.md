# Preserve the complete sample; one primary paired cost measurement per query

The fixed panel's119418coarse pairs make repeated large-pool inference dominate
runtime. Preserve all completed length-bucketed FP32 query blocks in phase1.
Continue EVERY unfinished original ID, unchanged checkpoint,backend,max256,
length bucketing,batch32,threads,cache,labels and16costIDs. No ID is removed or
replaced and no model output determines inclusion. Skip only fully completed
query blocks, with completion IDs fixed in the retained receipt before resuming.

For the remaining cost blocks use one measured U/P pairing in the same hash order.
The PRIMARY descriptive cost analysis uses repeat0 for ALL16queries, including
the early ones with two repeats. Keep extra early repeat1 observations separately;
do not selectively take best or median across unequal repeat counts. No timing
significance test, generalization or GPU speed claim is made. All128raw-U
predictions and20-request session traces remain planned. Each execution retains
the90-minute cap; phase provenance and all prior interrupted attempts remain.
