from chalk.features import features, Vector

@features
class MNISTDataPoint:
    id: int
    label: int  # 0-9
    split: str  # train or test
    pixels: Vector[784]