#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
FROM python:3.13-slim@sha256:f41a75c9cee9391c09e0139f7b49d4b1fbb119944ec740ecce4040626dc07bed

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
