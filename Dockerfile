#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
FROM python:3.12-slim@sha256:c24c34b502635f1f7c4e99dc09a2cbd85d480b7dcfd077198c6b5af138906390

WORKDIR /action/workspace
COPY requirements.txt CONTRIBUTING-template.md open_contrib_pr.py /action/workspace/

RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git-all=1:2.39.2-1.1 \
    && rm -rf /var/lib/apt/lists/*

CMD ["/action/workspace/open_contrib_pr.py"]
ENTRYPOINT ["python3", "-u"]

# To run ineractive debug on the docker container
# 1. Comment out the above CMD and ENTRYPOINT lines
# 2. Uncomment the ENTRYPOINT line below

#ENTRYPOINT ["bash"]
