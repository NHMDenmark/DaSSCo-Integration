## File-proxy: File serving and caching

File proxy can serve asset files to UIs and external publishers. There is caching of the files in order to serve files faster. The cache space is limited.

The data structure matches the ERDA structure:

[dassco-fileproxy-url]/files/assets/[institution]/[collection]/[asset-guid]/path/to/file

#### User access
Users must have access to the assets that the files belong to in order to see them.

#### Eviction
Cache eviction is based on the following [diagram](/documentation/diagrams/Unavngivet%20diagram-1722236945189.drawio)

Time: an entry can only stay in the cache for a certain amount of time. If the entry is used its lifetime is extended.

Disk space: Only a certain amount(not yet specified) of disk space is reserved for caching. If more than 90% of the reserved disk space is used entries closest to their expiration time will be evicted.

### Future improvements
#### Multi instance
Right now the cache eviction will run on all nodes if we start multiple nodes. This can cause concurrent access issue. Can probably be solved using SELECT FOR UPDATE in the database.

#### Role check
Currently we have to call ARS to check user access. If we do this from file-proxy instead we can remove a http call and save some time.

#### Optimize cache based on file size