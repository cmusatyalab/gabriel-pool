# Overview [![Docker Image Status][docker-image]][docker] [![License][license-image]][license]

A cognitive assistant that helps a pool player aim.

[docker-image]: https://img.shields.io/docker/build/cmusatyalab/gabriel-pool.svg
[docker]: https://hub.docker.com/r/cmusatyalab/gabriel-pool

[license-image]: http://img.shields.io/badge/license-Apache--2-blue.svg?style=flat
[license]: LICENSE

[playstore-badge]: https://play.google.com/intl/en_us/badges/images/generic/en_badge_web_generic.png
[playstore-link]: https://play.google.com/store/apps/details?id=edu.cmu.cs.gabrielclient
# Installation
## Client
An Android client is available on the Google PlayStore.

[![Google Play Store][playstore-badge]][playstore-link]

Google Play and the Google Play logo are trademarks of Google LLC.

## Server
Running the server application using Docker is advised. If you want to install from source, please see [Dockerfile](Dockerfile) for details.


# How to Run
## Client
From the main activity one can add servers by name and IP/domain. Subtitles for audio feedback can also been toggled. This option is useful for devices that may not have integrated speakers(like ODG R-7).
Pressing the 'Play' button next to a server will initiate a connection to the Gabriel server at that address.

## Server
### Container
```bash
nvidia-docker run --rm -it --name pool \
-p 0.0.0.0:9098:9098 -p 0.0.0.0:9111:9111 -p 0.0.0.0:22222:22222 \
-p 0.0.0.0:8080:8080 \
cmusatyalab/gabriel-pool:latest
```
