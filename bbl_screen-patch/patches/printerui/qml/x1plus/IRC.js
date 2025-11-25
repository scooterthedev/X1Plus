.pragma library
.import "Binding.js" as Binding

/* x1plusd IRC interface
 *
 * Copyright (c) 2025 Scooter Y.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

var X1Plus = null;

var [_messages, onMessages, _setMessages] = Binding.makeBinding([]);
var [_status, onStatus, _setStatus] = Binding.makeBinding({'connected': false});

function messages() {
    return _messages();
}

function status() {
    return _status();
}

function connect(server, port, nick, channel) {
    return X1Plus.DBus.proxyFunction("x1plus.x1plusd", "/x1plus/irc", "x1plus.irc", "Connect")({
        'server': server,
        'port': port,
        'nick': nick,
        'channel': channel
    })
}

function disconnect() {
    return X1Plus.DBus.proxyFunction("x1plus.x1plusd", "/x1plus/irc", "x1plus.irc", "Disconnect")({}); 
}

function sendMessage(message) {
    return X1Plus.DBus.proxyFunction("x1plus.x1plusd", "/x1plus/irc", "x1plus.irc", "SendMessage")({
        'message': message
    });
}

function awaken() {
    X1Plus.DBus.onSignal("x1plus.irc", "MessageReceived", function(msg) {
        var msgs = _messages();
        msgs.push(msg);
        _setMessages(msgs);
    });

    X1Plus.DBus.onSignal("x1plus.irc", "StatusChanged", (arg) => {
        _setStatus(arg);
    });
}