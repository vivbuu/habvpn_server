FROM ubuntu:22.04

RUN apt update && apt install -y wireguard python3 python3-pip iptables iproute2
RUN pip3 install flask requests

COPY server.py /app/server.py
COPY admin.html /app/admin.html
WORKDIR /app

CMD ["python3", "server.py"]
