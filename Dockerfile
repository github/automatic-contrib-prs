#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
FROM python:3.13-slim@sha256:4efa69bf17cfbd83a9942e60e2642335c3b397448e00410063a0421f9727c4c4

WORKDIR /action/workspace
COPY requirements.txt CONTRIBUTING-template.md open_contrib_pr.py /action/workspace/

RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git=1:2.39.5-0+deb12u1 \
    && rm -rf /var/lib/apt/lists/*

CMD ["/action/workspace/open_contrib_pr.py"]
ENTRYPOINT ["python3", "-u"]

# To run ineractive debug on the docker container
# 1. Comment out the above CMD and ENTRYPOINT lines
# 2. Uncomment the ENTRYPOINT line below

#ENTRYPOINT ["bash"]
