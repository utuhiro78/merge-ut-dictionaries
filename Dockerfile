FROM ruby:3.3.0

# Create working user
RUN useradd -ms /bin/bash ubuntu
USER ubuntu
WORKDIR /home/ubuntu/

# Copy code
WORKDIR /home/ubuntu/work/
COPY ./src/ ./

ENTRYPOINT [ "/bin/bash" ]
