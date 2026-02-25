-- Example SQL resolver to retrieve the test set for MNIST.
-- resolves: MNISTDataPoint
-- source: postgres
-- tags: ['test']

select
    id,
    label,
    split,
    pixels
from mnist
WHERE split = 'test'