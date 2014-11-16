#! /bin/bash
# build hoocal prod

gulp env:prod path:hoocal clean
gulp env:prod path:hoocal pipe:res
gulp env:prod path:hoocal pipe:views