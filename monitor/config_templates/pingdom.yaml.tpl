# Stream configurations
stream:
  # Which stream to use
  source: pingdom

# Pingdom credentials
credentials:
    username: USERNAME
    password: PASSWORD
    appkey: APPKEY

# [Optional] Monitors parameters. Have defaults if we omit it, as shown below.
parameters:
    # Resolution of NuPIC RandomDistributedScalarEncoder to use
    encoder_resolution: 1

    # Time sleep between requests when it's in online learning
    seconds_per_request: 60

    # How many points to use for data smoothing when doing averaging
    moving_average_window: 1

    # Factor to multiply each data value when using scale transform
    scaling_factor: 1

    # Thresholds that triggers a POST to the webhook (if supplied)
    likelihood_threshold: None
    anomaly_threshold: None

# [Optional ] Domain in which you'll be running the service.
# This will be used to create links to anomalous monitors when reporting anomalies.
# If not specified we'll use "localhost".
domain: omg-monitor.ai

# [Optional]  An endpoint that will receive POST request when something above
# the defined thresholds is found. We post a JSON with the following structure:
#
#{
#    "sent_at": "2014-09-04T14:42:18.560047",
#    "monitor": "check_name",
#    "source": "PingdomStream",
#    "metric": "Response time",
#    "report": {
#        "status": "Entering anomalous state"
#        "anomaly_score": 1,
#        "likelihood": 0.841344746,
#        "model_input": {
#            "time": "2014-09-04T14:41:26",
#            "value": 716
#        },
#    }
#}
webhook: http://localhost/listening

# [Optional] A list with checks to monitor. If not supplied, we run everything.
monitors: [123456, 875642]
