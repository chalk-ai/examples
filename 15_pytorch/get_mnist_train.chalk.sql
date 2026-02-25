-- Example SQL resolver to retrieve the training set for MNIST.
-- resolves: MNISTDataPoint
-- source: postgres
-- tags: ['train']

select
    id,
    label,
    split,
    pixels
from mnist
WHERE split = 'train'