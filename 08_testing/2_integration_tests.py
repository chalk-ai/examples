# You can apply changes with the `--no-promote`
# flag to create a preview environment:
#
# > chalk apply --no-promote

# Once your code has been deployed, you can query
# the resulting deployment id:
#
# > chalk query --deployment $DEPLOYMENT_ID \
#               --in user.id=1 \
#               --out user.id \
#               --out user.email
