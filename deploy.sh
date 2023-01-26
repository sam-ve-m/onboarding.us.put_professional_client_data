fission spec init
fission env create --spec --name onb-us-job-env --image nexus.sigame.com.br/fission-onboarding-us-job:0.1.0 --poolsize 2 --graceperiod 3 --version 3 --imagepullsecret "nexus-v3" --spec
fission fn create --spec --name onb-us-job-fn --env onb-us-job-env --code fission.py --executortype poolmgr --requestsperpod 10000 --spec
fission route create --spec --name onb-us-job-rt --method PUT --url /onboarding/employ_for_us --function onb-us-job-fn