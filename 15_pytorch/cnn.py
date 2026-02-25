from chalk.client import ChalkClient
from features import MNISTDataPoint
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data
from torch.autograd import Variable

def evaluate(model, test_loader):
    correct = 0
    for batch_idx, batch in enumerate(test_loader):
        # The example vector we retrieve from the Chalk dataset is flattened, we reshape to an image format here.

        # Rows/batches in torch datasets produced from Chalk are dictionary-based, which use the feature FQNs.
        x_batch = Variable(batch[str(MNISTDataPoint.pixels)]).float().reshape([test_loader.batch_size, 1, 28, 28])
        y_batch = Variable(batch[str(MNISTDataPoint.label)])

        # Make predictions
        output = model(x_batch)

        # Measure testing accuracy
        predictions = torch.max(output.data, 1)[1]
        correct += (predictions == y_batch).sum()
        if (batch_idx+1) % 50 == 0:
            # Print a progress report every 50 batches
            print('TESTING: [{}/{} ({:.0f}%)]\t Accuracy:{:.3f}%'.format(
                batch_idx*test_loader.batch_size,
                len(test_loader.dataset),
                100.*batch_idx / len(test_loader),
                float(correct*100) / float(test_loader.batch_size*(batch_idx+1)))
            )

def fit(model, train_loader):
    optimizer = torch.optim.Adam(model.parameters())
    error = nn.CrossEntropyLoss()
    EPOCHS = 3
    model.train()
    for epoch in range(EPOCHS):
        correct = 0
        for batch_idx, batch in enumerate(train_loader):
            # The example vector we retrieve from the Chalk dataset is flattened, we reshape to an image format here.

            # Rows/batches in torch datasets produced from Chalk are dictionary-based, which use the feature FQNs.
            x_batch = Variable(batch[str(MNISTDataPoint.pixels)]).float().reshape([train_loader.batch_size, 1, 28, 28])
            y_batch = Variable(batch[str(MNISTDataPoint.label)])

            # Perform the training and do backpropagation over the loss
            optimizer.zero_grad()
            output = model(x_batch)
            loss = error(output, y_batch)
            loss.backward()
            optimizer.step()

            # Measure training accuracy
            predictions = torch.max(output.data, 1)[1]
            correct += (predictions == y_batch).sum()
            if (batch_idx+1) % 50 == 0:
                # Print a progress report every 50 batches
                print('Epoch : {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}\t Accuracy:{:.3f}%'.format(
                    epoch,
                    batch_idx*train_loader.batch_size,
                    len(train_loader.dataset),
                    100.*batch_idx / len(train_loader),
                    loss.item(),
                    float(correct*100) / float(train_loader.batch_size*(batch_idx+1)))
                )

class CNN(nn.Module):
    """
    Simple convolution neural network architecture with max pooling.
    """
    def __init__(self):
        super(CNN, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, kernel_size=5)
        self.conv2 = nn.Conv2d(32, 32, kernel_size=5)
        self.conv3 = nn.Conv2d(32,64, kernel_size=5)
        self.fc1 = nn.Linear(3*3*64, 256)
        self.fc2 = nn.Linear(256, 10)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(F.max_pool2d(self.conv2(x), 2))
        x = F.dropout(x, p=0.5, training=self.training)
        x = F.relu(F.max_pool2d(self.conv3(x),2))
        x = F.dropout(x, p=0.5, training=self.training)
        x = x.view(-1,3*3*64 )
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x, dim=1)


cnn = CNN()
client = ChalkClient()

"""
Running an offline query to retrieve the training dataset. We use the "train" tag to mark that we want to use
the SQL in get_mnist_train.chalk.sql as our root resolver, and use create_torch_map_dataset() to generate a 
Torch dataset.

Learn more about Chalk datasets at https://docs.chalk.ai/docs/datasets.
"""
print("Loading train dataset from Chalk...")

train_ds = client.offline_query(
    output=[MNISTDataPoint],
    max_samples=60_000,
    tags=['train'],
    recompute_features=True,
)
torch_train_ds = train_ds.create_torch_map_dataset()

print("Loaded train dataset from Chalk.")

"""
Create a dataloader from the Torch dataset. Since we are using a map-based dataset, we can set shuffle=True, which
helps the model generalize instead of learning patterns within the order of the dataset itself across epochs.
"""
train_dl = torch.utils.data.DataLoader(torch_train_ds, batch_size=100, shuffle=True)
fit(cnn, train_dl)


"""
Running an offline query to retrieve the testing dataset. We use the "test" tag to mark that we want to use
the SQL in get_mnist_test.chalk.sql as our root resolver, and use create_torch_iter_dataset() to generate a 
Torch dataset.
"""
print("Loading test dataset from Chalk...")
test_ds = client.offline_query(
    output=[MNISTDataPoint],
    max_samples=10_000,
    tags=['test'],
    recompute_features=True,
)
torch_test_ds = test_ds.create_torch_iter_dataset()

print("Loaded test dataset from Chalk.")

"""
Create a dataloader from the Torch dataset. create_torch_iter_dataset() creates an iterable dataset, which does not
allow for shuffle but is not necessary here as we are testing and not modifying the model at this point. For larger
datasets, it is preferable to use the iterable pattern, as they do not load the entire dataset into memory.
"""
test_dl = torch.utils.data.DataLoader(torch_test_ds)
evaluate(cnn, test_dl)