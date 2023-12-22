# konbinein

## development

### dependencies

- [docker](https://www.docker.com/)
- [pre-commit](https://github.com/pre-commit/pre-commit)

### setup

```shell
pre-commit install
```

### start app

```shell
docker compose up -d
```

### stop app

```shell
docker compose down
```

### start shell for command

```shell
docker exec -it konbinein-app-1 bash
poetry shell
```

### run command

```shell
docker exec -it konbinein-app-1 bash -c "poetry run <command>"
```

### rebuild image (to migrate, add/update/remove packages, etc.)

```shell
docker image rm konbinein-app
docker builder prune -f
```
