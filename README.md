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

### add package
```shell
docker exec -it konbinein-app-1 bash
poetry run add package
# must also remove image and clear build cache
```

### remove image and clear build cache
```shell
docker image rm konbinein-app
docker builder prune -f
```
