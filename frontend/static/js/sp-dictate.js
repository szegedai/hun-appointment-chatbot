function SpeechtexAsrHandler() {
    this.controlReceived = function (msg) {
        console.log('MSG: [' + msg.type + '] ' + msg.msg + ' (' + msg.params + ')');
    }
    this.errorReceived = function (msg) {
        console.log('MSG: [' + msg.type + '] ' + msg.msg + ' (' + msg.params + ')');
    }
    this.resultReceived = function (msg) {
        console.log('MSG: [' + msg.type + '] ' + msg.msg + ' (' + msg.params + ')');
    }
};

function SpeechtexMessage(raw_msg) {
    this.type;
    this.msg;
    this.params = new Array();

    if (raw_msg.indexOf('|') > -1) {
        this.type = raw_msg.substring(0, raw_msg.indexOf('|'));
        if (raw_msg.indexOf(';') > -1) {
            this.msg = raw_msg.substring(raw_msg.indexOf('|') + 1,

                raw_msg.indexOf(';'));

            raw_msg = raw_msg.substring(raw_msg.indexOf(';') + 1);
            this.params = raw_msg.split(';');
        } else {
            this.msg = raw_msg.substring(raw_msg.indexOf('|') + 1);
        }
    }

}

/*
SpeechTex connection object
*/
function SpeechtexAsrConnection(wsProxyUrl) {
    // Input uzenetek
    const MSG_IN_GENERAL_CONTROL = 'control|';
    const MSG_IN_BIND_OK = 'control|bind-ok';
    const MSG_IN_BIND_FAILED = 'control|bind-failed';
    const MSG_IN_BIND_CONNECT_FAILED = 'control|connect-failed';
    const MSG_IN_LOOPBACK_ID = 'control|loopback-id';
    const MSG_IN_LOOPBACK_STATUS = 'control|loopback-status';
    // Output uzenetek
    const MSG_OUT_RECOG_START = 'control|start';
    const MSG_OUT_RECOG_STOP = 'control|stop';
    const MSG_OUT_BIND_REQUEST = 'control|bind-request';
    const MSG_OUT_DISCONNECT = 'control|disconnect';
    const MSG_OUT_CREATE_LOOPBACK = 'control|create-loopback';
    const MSG_OUT_GET_MODELS = 'control|get-models';

    var ws;
    var asrBindOk = false;
    var recording = false;
    var sampleRate = 48000;
    var loopbackId = '';
    var wsProxyUrl = wsProxyUrl;
    var handler;

    var statusInterval;

    this.connect = function () {
        ws = new WebSocket(wsProxyUrl);
        this.init();
        ws.onmessage = function (e) {
            var msg = e.data;
            // Sikeres ASR kapcsolodas
            if (msg == MSG_IN_BIND_OK)
                asrBindOk = true;
            // loopback id beallitasa
            else if (msg.indexOf(MSG_IN_LOOPBACK_ID) > -1) {
                loopbackId = msg.substring(msg.indexOf(';') + 1);
            }
            // loopback status uzenetek
            else if (msg.indexOf(MSG_IN_LOOPBACK_STATUS) > -1) {
                var status = parseInt(msg.substring(msg.lastIndexOf(';') + 1));
                if (status != 0) {
                    clearInterval(statusInterval);
                    statusInterval = undefined;
                }
            }
            propagate(msg);
        }
    }
    this.setHandler = function (h) {
        handler = h;
    }
    propagate = function (msg) {
        var spMsg = new SpeechtexMessage(msg);
        if (!(handler == null) && spMsg.type === 'error' &&

            typeof (handler.errorReceived) == "function")
            handler.errorReceived(spMsg);
        else if (!(handler == null) && spMsg.type === 'result' &&

            typeof (handler.resultReceived) == "function")
            handler.resultReceived(spMsg);
        else if (!(handler == null) && spMsg.type === 'control' &&

            typeof (handler.controlReceived) == "function")
            handler.controlReceived(spMsg);

    }
    this.init = function () {
        if (hasGetUserMedia()) {
            navigator.getUserMedia({ video: false, audio: true }, function (localMediaStream) {
                var audioContext = window.AudioContext;
                var context = new audioContext();
                var source = context.createMediaStreamSource(localMediaStream);
                sampleRate = context.sampleRate;
                if (!context.createScriptProcessor) {
                    node = context.createJavaScriptNode(0, 1, 1);
                } else {
                    node = context.createScriptProcessor(0, 1, 1);
                }
                node.onaudioprocess = function (e) {
                    if (recording) {
                        sendAudioData(e.inputBuffer.getChannelData(0));
                    }
                };
                source.connect(node);
                node.connect(context.destination);
            }, this.getUserMediaError);
        }
    }
    this.getUserMediaError = function (e) {
    };
    this.disconnect = function () {
        if (!(ws == null))
            ws.close();

    }
    sendControl = function (control) {
        if (!(ws == null))
            ws.send(control);
        else
            propagate('error|001;No connection to Speechtex ASR Proxy.');

    }
    sendAudioData = function (data) {

        if (!data)
            return -1;
        var len = data.length, i = 0;
        var dataAsInt16Array = new Int16Array(len);
        while (i < len)
            dataAsInt16Array[i] = convert(data[i++]);

        if (!(ws == null))
            ws.send(dataAsInt16Array);
        return 1;
    }
    /*
    Csatlakozas adott modellt futtato felismero csatornahoz
    */
    this.bindAsrChannel = function (model) {
        sendControl(MSG_OUT_DISCONNECT);
        sendControl(MSG_OUT_BIND_REQUEST + ';' + model);
    }
    /*
    Felismeres inditasa
    */
    this.startRecognition = function () {
        if (!asrBindOk) {
            return;
        }
        //console.log(MSG_OUT_RECOG_START + ";" + sampleRate + ";" + loopbackId);
        sendControl(MSG_OUT_RECOG_START + ";" + sampleRate + ";" + loopbackId + ";0;");

        recording = true;
    }
    this.stopRecognition = function () {
        sendControl(MSG_OUT_RECOG_STOP + ";");

        recording = false;
    }
    this.generateLoopback = function (dic) {
        var params = '';
        if (Array.isArray(dic)) {
            for (i = 0; i < dic.length; i++) {
                var dici = dic[i];
                if (Array.isArray(dici) && dici.length >= 2) {

                    if (params !== '')
                        params += ";";
                    params += dici[0] + "=" + dici[1];
                }
            }
        }

        sendControl(MSG_OUT_CREATE_LOOPBACK + ";" + params);
    }
    this.getModels = function () {
        sendControl(MSG_OUT_GET_MODELS);
    }
}

/*
Egyeb szukseges metodusok
*/
navigator.getUserMedia = navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia;
function hasGetUserMedia() {
    return !!(navigator.getUserMedia || navigator.webkitGetUserMedia ||
        navigator.mediaDevices.getUserMedia || navigator.msGetUserMedia);
}
function convert(n) {
    var v = n * 32768;
    return Math.max(-32767, Math.min(32767, v));
}