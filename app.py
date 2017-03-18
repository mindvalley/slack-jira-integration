#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask
from flask import request
from flask import make_response

from urllib.parse import urlencode
from urllib.request import Request, urlopen

from jira import JIRA

jira = JIRA("https://mindvalley.atlassian.net", basic_auth=('andre', 'zaqwsx123!@#'))


# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    newTicket = createTicket(req)
    if newTicket is None:
        return {}
    res = makeWebhookResult(newTicket)
    return res


def createTicket(req):

    #read request
    contexts = req.get("contexts")
    print(json.dumps(contexts))
    for context in contexts:
        if (context.get("name") == "creating-ticket") :
            result = req.get("contexts")[0]
            title = result.get("title")
            team = result.get("team")
            issueTypeName = result.get("ticket")[0]
            action = result.get("action")
            expected = result.get("expected")
            actual = result.get("actual")
            projectName = "SLACK"

            new_issue = jira.create_issue(
                project='SLACK',
                summary=title,
                description='"description": "Steps taken:%s"\n\nExpected Behavior: %s\n\nActual Behavior: %s,"issuetype": {"name": "%s"} }}' % (title, action, expected, actual),
                issuetype={'name': issueTypeName})

            return new_issue

    return None

def makeWebhookResult(newTicket):

    # for field in newTicket.raw['fields']:
    #     print("Field:", field, "Value:", newTicket.raw['fields'][field])

    speech = "Ticket created: " +newTicket

    return {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-jira-mindvalley-integration"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    #payload = {"somekey":'somevalue'}

    #json.dumps(payload)

    #request.post('localhost:5000', data=payload)

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='localhost')
