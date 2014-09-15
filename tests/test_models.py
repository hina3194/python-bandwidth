import responses
import unittest

from bandwith_sdk import Call, Bridge, BandwithError, Application


def assertJsonEq(first, second, msg='Ouups'):
    assert sorted(first) == sorted(second), '%r != %r\n%s' % (first, second, msg)


class CallsTest(unittest.TestCase):

    @responses.activate
    def test_get(self):
        """
        Call.get('by-call-id')
        """
        raw = """
        {
        "id": "c-call-id",
        "direction": "out",
        "from": "+1919000001",
        "to": "+1919000002",
        "recordingEnabled": false,
        "callbackUrl": "",
        "state": "active",
        "startTime": "2013-02-08T13:15:47.587Z",
        "activeTime": "2013-02-08T13:15:52.347Z",
        "events": "https://.../calls/{callId}/events"
        }
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/c-call-id',
                      body=raw,
                      status=201,
                      content_type='application/json')
        call = Call.get('c-call-id')

        self.assertEqual(call.call_id, 'c-call-id')
        self.assertEqual(call.direction, 'out')
        self.assertEqual(call.from_, '+1919000001')
        self.assertEqual(call.to, '+1919000002')
        self.assertEqual(call.recording_enabled, False)
        self.assertEqual(call.state, 'active')

    @responses.activate
    def test_get_and_not_found(self):
        """
        Not found Call.get('by-call-id')
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/c-call-id',
                      body='',
                      status=404,
                      content_type='application/json')
        with self.assertRaises(BandwithError) as be:
            Call.get('c-call-id')
        the_exception = be.exception
        self.assertEqual(str(the_exception), '404 Client Error: None')

    @responses.activate
    def test_list(self):
        """
        Call.list()
        """
        raw = """
        [{
        "id": "c-call-id",
        "direction": "out",
        "from": "+1919000001",
        "to": "+1919000002",
        "recordingEnabled": false,
        "callbackUrl": "",
        "state": "active",
        "startTime": "2013-02-08T13:15:47.587Z",
        "activeTime": "2013-02-08T13:15:52.347Z",
        "events": "https://.../calls/{callId}/events"
        },
        {
        "id": "c-call-id-1",
        "direction": "out",
        "from": "+1919000001",
        "to": "+1919000002",
        "recordingEnabled": false,
        "callbackUrl": "",
        "state": "active",
        "startTime": "2013-02-08T13:15:47.587Z",
        "activeTime": "2013-02-08T13:15:52.347Z",
        "events": "https://.../calls/{callId}/events"
        }
        ]
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls',
                      body=raw,
                      status=200,
                      content_type='application/json')
        calls = Call.list()

        self.assertEqual(calls[0].call_id, 'c-call-id')
        self.assertEqual(calls[1].call_id, 'c-call-id-1')

    @responses.activate
    def test_create(self):
        """
        Call.create("+1919000001", "+1919000002")
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/new-call-id'})

        call = Call.create("+1919000001", "+1919000002")

        self.assertEqual(call.call_id, 'new-call-id')

    @responses.activate
    def test_play_audio(self):
        """
        Call('new-call-id').play_audio('Hello.mp3')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/audio',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/new-call-id'})

        call = Call('new-call-id')
        call.play_audio('Hello.mp3', loop_enabled=True, tag='custom_tag')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"loopEnabled": true, "tag": "custom_tag", "fileUrl": "Hello.mp3"}')

    @responses.activate
    def test_stop_audio(self):
        """
        Call('new-call-id').stop_audio()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/audio',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        call.stop_audio()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"fileUrl": ""}')

    @responses.activate
    def test_speak_sentence(self):
        """
        Call('new-call-id').speak_sentence('Hello', gender='female')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/audio',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/new-call-id'})

        call = Call('new-call-id')
        call.speak_sentence('Hello', gender='female', voice='Jorge', loop_enabled=True)
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"voice": "Jorge", "sentence": "Hello", "gender": "female", "loopEnabled": true}')

    @responses.activate
    def test_stop_sentence(self):
        """
        Call('new-call-id').stop_sentence()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/audio',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        call.stop_sentence()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"sentence": ""}')

    @responses.activate
    def test_transfer(self):
        """
        Call('new-call-id').transfer('+1919000008', whisper_audio={"sentence": "Hello {number}, thanks for calling"})
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/calls/tr-call-id'})

        call = Call('new-call-id')
        new_call = call.transfer('+1919000008', whisper_audio={"sentence": "Hello {number}, thanks for calling"})
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"transferTo": "+1919000008", "state": "transferring", '
                                      '"whisperAudio": {"sentence": "Hello {number}, thanks for calling"}}')

        self.assertIsInstance(new_call, Call)
        self.assertEqual(new_call.call_id, 'tr-call-id')

    @responses.activate
    def test_hangup(self):
        """
        Call('new-call-id').hangup()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        call.hangup()
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"state": "completed"}')

        self.assertEqual(call.state, 'completed')

    @responses.activate
    def test_send_dtmf(self):
        """
        Call('new-call-id').send_dtmf('121')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/dtmf',
                      body='',
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        call.send_dtmf('121')
        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"dtmfOut": "121"}')

    @responses.activate
    def test_get_events(self):
        """
        Call('new-call-id').get_events()
        """
        raw = """
        [
        {
        "id": "{callEventId1}",
        "time": "2012-09-19T13:55:41.343Z",
        "name": "create"
        },
        {
        "id": "{callEventId2}",
        "time": "2012-09-19T13:55:45.583Z",
        "name": "answer"
        },
        {
        "id": "{callEventId3}",
        "time": "2012-09-19T13:55:45.583Z",
        "name": "hangup",
        "data": "foo"
        }]
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/new-call-id/events',
                      body=raw,
                      status=200,
                      content_type='application/json',
                      )

        call = Call('new-call-id')
        events = call.get_events()
        self.assertEqual(len(events), 3)

    @responses.activate
    def test_refresh(self):
        """
        Call('c-call-id').refresh()
        """
        raw = """
        {
        "id": "c-call-id",
        "direction": "out",
        "from": "+1919000001",
        "to": "+1919000002",
        "recordingEnabled": false,
        "callbackUrl": "",
        "state": "active",
        "startTime": "2013-02-08T13:15:47.587Z",
        "activeTime": "2013-02-08T13:15:52.347Z",
        "events": "https://.../calls/{callId}/events"
        }
        """
        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/calls/c-call-id',
                      body=raw,
                      status=200,
                      content_type='application/json',
                      )

        call = Call('c-call-id')
        call.refresh()
        self.assertEqual(call.call_id, 'c-call-id')
        self.assertEqual(call.direction, 'out')
        self.assertEqual(call.from_, '+1919000001')
        self.assertEqual(call.to, '+1919000002')
        self.assertEqual(call.recording_enabled, False)
        self.assertEqual(call.state, 'active')


class BridgesTest(unittest.TestCase):

    @responses.activate
    def test_get(self):
        """
        Bridge.get('by-bridge-id')
        """
        raw = """
        {
        "id": "by-bridge-id",
        "state": "completed",
        "bridgeAudio": "true",
        "calls":"https://.../v1/users/{userId}/bridges/{bridgeId}/calls",
        "createdTime": "2013-04-22T13:55:30.279Z",
        "activatedTime": "2013-04-22T13:55:30.280Z",
        "completedTime": "2013-04-22T13:59:30.122Z"
        }
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/by-bridge-id',
                      body=raw,
                      status=201,
                      content_type='application/json')
        bridge = Bridge.get('by-bridge-id')

        self.assertIsInstance(bridge, Bridge)

        self.assertEqual(bridge.id, 'by-bridge-id')

    @responses.activate
    def test_get_and_not_found(self):
        """
        Not found Bridge.get('by-bridge-id')
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges/by-bridge-id',
                      body='',
                      status=404,
                      content_type='application/json')
        with self.assertRaises(BandwithError) as be:
            Bridge.get('by-bridge-id')
        the_exception = be.exception
        self.assertEqual(str(the_exception), '404 Client Error: None')

    @responses.activate
    def test_list(self):
        """
        Bridge.list()
        """
        raw = """
        [
          {
            "id": "bridge-1",
            "state": "completed",
            "bridgeAudio": "true",
            "calls":"https://.../v1/users/{userId}/bridges/{bridgeId}/calls",
            "createdTime": "2013-04-22T13:55:30.279Z",
            "activatedTime": "2013-04-22T13:55:30.280Z",
            "completedTime": "2013-04-22T13:56:30.122Z"
          },
          {
            "id": "bridge-2",
            "state": "completed",
            "bridgeAudio": "true",
            "calls":"https://.../v1/users/{userId}/bridges/{bridgeId}/calls",
            "createdTime": "2013-04-22T13:58:30.121Z",
            "activatedTime": "2013-04-22T13:58:30.122Z",
            "completedTime": "2013-04-22T13:59:30.122Z"
          }
        ]

        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges',
                      body=raw,
                      status=200,
                      content_type='application/json')
        bridges = Bridge.list()

        self.assertEqual(bridges[0].id, 'bridge-1')
        self.assertEqual(bridges[1].id, 'bridge-2')

    @responses.activate
    def test_create(self):
        """
        Bridge.create()
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/bridges/new-bridge-id'})

        bridge = Bridge.create()
        self.assertIsInstance(bridge, Bridge)
        self.assertEqual(bridge.id, 'new-bridge-id')

    @responses.activate
    def test_create_form_call(self):
        """
        Bridge.create(Call('c-foo'), Call('c-bar')))
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/bridges',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/bridges/new-bridge-id'})

        bridge = Bridge.create(Call('c-foo'), Call('c-bar'))
        self.assertIsInstance(bridge, Bridge)
        self.assertEqual(bridge.id, 'new-bridge-id')

        request_message = responses.calls[0].request.body
        assertJsonEq(request_message, '{"callIds": ["c-foo", "c-bar"]}')

    def test_calls_property(self):
        """
        Bridge('bridge-id').calls
        """

        bridge = Bridge('bridge-id', Call('c-foo'), Call('c-bar'))

        self.assertIsInstance(bridge, Bridge)
        self.assertEqual(bridge.id, 'bridge-id')

        calls = bridge.calls

        self.assertEqual(calls[0].call_id, 'c-foo')
        self.assertEqual(calls[1].call_id, 'c-bar')


class ApplicationsTest(unittest.TestCase):

    @responses.activate
    def test_get(self):
        """
        Application.get('by-application_id')
        """
        raw = """
        {
        "id": "a-application-id",
        "callbackHttpMethod": "post",
        "incomingCallUrl": "http://callback.info",
        "name": "test_application_name",
        "autoAnswer": true
        }
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/a-application-id',
                      body=raw,
                      status=200,
                      content_type='application/json')
        application = Application.get('a-application-id')

        self.assertEqual(application.application_id, 'a-application-id')
        self.assertEqual(application.incoming_call_url, 'http://callback.info')
        self.assertEqual(application.callback_http_method, 'post')
        self.assertEqual(application.name, 'test_application_name')
        self.assertEqual(application.auto_answer, True)

    @responses.activate
    def test_get_and_not_found(self):
        """
        Not found Application.get('by-application_id')
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/c-call-id',
                      body='',
                      status=404,
                      content_type='application/json')
        with self.assertRaises(BandwithError) as be:
            Application.get('c-call-id')
        the_exception = be.exception
        self.assertEqual(str(the_exception), '404 Client Error: None')

    @responses.activate
    def test_list(self):
        """
        Application.list()
        """
        raw = """
        [{
        "id": "a-application-id",
        "callbackHttpMethod": "post",
        "incomingCallUrl": "http://callback.info",
        "name": "test_application_name",
        "autoAnswer": true
        },
        {
        "id": "a-application-id1",
        "callbackHttpMethod": "get",
        "incomingCallUrl": "http://callback1.info",
        "name": "test_application_name1",
        "autoAnswer": false
        }
        ]
        """

        responses.add(responses.GET,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/',
                      body=raw,
                      status=200,
                      content_type='application/json')
        applications = Application.list()

        self.assertEqual(applications[0].application_id, 'a-application-id')
        self.assertEqual(applications[0].incoming_call_url, 'http://callback.info')
        self.assertEqual(applications[0].callback_http_method, 'post')
        self.assertEqual(applications[0].name, 'test_application_name')
        self.assertEqual(applications[0].auto_answer, True)
        self.assertEqual(applications[1].application_id, 'a-application-id1')
        self.assertEqual(applications[1].incoming_call_url, 'http://callback1.info')
        self.assertEqual(applications[1].callback_http_method, 'get')
        self.assertEqual(applications[1].name, 'test_application_name1')
        self.assertEqual(applications[1].auto_answer, False)

    @responses.activate
    def test_create(self):
        """
        Application.create(name='new-application', incoming_call_url='http://test.callback.info')
        """
        responses.add(responses.POST,
                      'https://api.catapult.inetwork.com/v1/users/u-user/applications/',
                      body='',
                      status=201,
                      content_type='application/json',
                      adding_headers={'Location': '/v1/users/u-user/applications/new-application-id'})

        application = Application.create(name='new-application', incoming_call_url='http://test.callback.info')

        self.assertEqual(application.application_id, 'new-application-id')
        self.assertEqual(application.incoming_call_url, 'http://test.callback.info')
        self.assertEqual(application.callback_http_method, 'post')
        self.assertEqual(application.name, 'new-application')
        self.assertEqual(application.auto_answer, True)
