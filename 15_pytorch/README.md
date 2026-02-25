## Integrating Datasets with Pytorch

When working with [PyTorch](https://pytorch.org/), you can use the resulting dataset of an offline query to
produce a PyTorch dataset directly via `Dataset.create_torch_map_dataset()` and `Dataset.create_torch_iter_dataset()`.

```python
import torch.utils.data

ds = ChalkClient().offline_query(
    outputs=[User.id, User.name, User.preferences],
    max_samples=100000,
)
torch_dataset = ds.create_torch_map_dataset()
torch_dataloader = torch.utils.data.DataLoader(torch_dataset, shuffle=True)
```

If you find yourself repeating the same pattern for many of these resolvers, codegen
can be helpful to dry up your definitions.