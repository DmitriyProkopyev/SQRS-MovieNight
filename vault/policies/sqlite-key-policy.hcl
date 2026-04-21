path "secret/data/movienight/sqlite" {
  capabilities = ["create", "read", "update"]
}

path "secret/metadata/movienight/sqlite" {
  capabilities = ["read", "list"]
}