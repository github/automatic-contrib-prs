#checkov:skip=CKV_DOCKER_2
#checkov:skip=CKV_DOCKER_3
FROM python:3.13-slim@sha256:f3614d98f38b0525d670f287b0474385952e28eb43016655dd003d0e28cf8652

WORKDIR /action/workspace
COPY requirements.txt CONTRIBUTING-template.md open_contrib_pr.py /action/workspace/

RUN python3 -m pip install --no-cache-dir -r requirements.txt \
    && apt-get -y update \
    && apt-get -y install --no-install-recommends git=1:2.39.5-0+deb12u2 \
    && rm -rf /var/lib/apt/lists/*

CMD ["/action/workspace/open_contrib_pr.py"]
ENTRYPOINT ["python3", "-u"]

# To run ineractive debug on the docker container
# 1. Comment out the above CMD and ENTRYPOINT lines
# 2. Uncomment the ENTRYPOINT line below

#ENTRYPOINT ["bash"]
