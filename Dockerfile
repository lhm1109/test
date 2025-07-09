ARG DEBIAN_VERSION=bookworm
ARG DIRECTORY=streamlit
ARG PORT_NUMBER=7172

# Set Parent image : python
FROM python:3.10-slim-$DEBIAN_VERSION

LABEL MAINTAINER "kjb0913@midasit.com"

RUN mkdir /usr/streamlit

# Set Workdir
WORKDIR /usr/streamlit

# Install required packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir streamlit pandas numpy matplotlib

# Add Source
COPY streamlit/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get update && apt-get install -y procps

COPY streamlit .

# Add Port
EXPOSE 7172

# Execute
CMD [ "streamlit", "run", "--client.showSidebarNavigation=False", "--client.toolbarMode=minimal", "--ui.hideTopBar=true", "app.py", "--server.port=7172", "--server.address=0.0.0.0" ] 
