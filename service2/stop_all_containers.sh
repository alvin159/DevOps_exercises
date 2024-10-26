# stop_all_containers.sh
#!/bin/bash
docker ps -q | xargs -I {} docker stop {}