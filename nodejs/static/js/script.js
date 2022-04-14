// ========================== greet user proactively ========================
var ID = function () {
  // Math.random should be unique because of its seeding algorithm.
  // Convert it to base 36 (numbers + letters), and grab the first 9 characters
  // after the decimal.
  return '_' + Math.random().toString(36).substr(2, 9);
};

$(document).ready(function () {
  $('.profile_div').toggle();
  $('.widget').toggle();
  //drop down menu for close, restart conversation & clear the chats.
  $('.dropdown-trigger').dropdown();

  //initiate the modal for displaying the charts, if you dont have charts, then you comment the below line
  $('.modal').modal();

  //enable this if u have configured the bot to start the conversation.
  showBotTyping();
  $('#userInput').prop('disabled', true);

  //global variables
  //action_name = "action_greet_user";
  PORT = '3005';
  user_id = ID();
  console.log(user_id);
  //if you want the bot to start the conversation
  action_trigger();
  //Set cursor in textarea
  $('#userInput').focus();
});

// ========================== restart conversation ========================
function restartConversation() {
  $('#userInput').prop('disabled', true);
  //destroy the existing chart
  $('.collapsible').remove();

  if (typeof chatChart !== 'undefined') {
    chatChart.destroy();
  }

  $('.chart-container').remove();
  if (typeof modalChart !== 'undefined') {
    modalChart.destroy();
  }
  $('.chats').html('');
  $('.usrInput').val('');
  send('/restart');
}

$('#feedback-btn').on('click', function () {
  text = $('#feedback').val();
  date = new Date().toLocaleString();

  $.ajax({
    url: 'https://chatbot-rgai3.inf.u-szeged.hu/mongo',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
      user_id: user_id,
      description: text,
      createdAt: date
    }),
    success: function () {
      console.log('Sikeres visszajelzés!');
      $('#feedback').val('');
      $('#result').text('Sikeres visszajelzés');
    },
    error: function () {
      console.log('Hiba történt az adatbázisba való feltöltés során.');
      $('#feedback').val('');
      $('#result').text('Hiba történt az adatbázisba való feltöltés során.');
    }
  });
});

// Not actually triggering action as it would always create a new mongodb instance
function action_trigger() {
  let msg;
  setTimeout(function () {
    hideBotTyping();
    msg =
      'Jó napot! Főnök Úr virtuális személyi asszisztense vagyok, én kezelem a naptárában az időpont foglalásokat. Mikorra szeretne hozzá időpontot?';
    var BotResponse =
      '<img class="botAvatar" src="https://chatbot-rgai3.inf.u-szeged.hu/img/botAvatar.png"/><p class="botMsg">' +
      msg +
      '</p><div class="clearfix"></div>';
    $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
    scrollToBottomOfResults();
  }, 500);
  //tts(msg);
  $('#userInput').prop('disabled', false);
}

//=====================================	user enter or sends the message =====================
$('.usrInput').on('keyup keypress', function (e) {
  var keyCode = e.keyCode || e.which;

  var text = $('.usrInput').val();
  if (keyCode === 13) {
    if (text == '' || $.trim(text) == '') {
      e.preventDefault();
      return false;
    } else {
      //destroy the existing chart, if yu are not using charts, then comment the below lines
      $('.collapsible').remove();
      if (typeof chatChart !== 'undefined') {
        chatChart.destroy();
      }

      $('.chart-container').remove();
      if (typeof modalChart !== 'undefined') {
        modalChart.destroy();
      }

      $('#paginated_cards').remove();
      $('.suggestions').remove();
      $('.quickReplies').remove();
      $('.usrInput').focus();
      setUserResponse(text);
      send(text);
      e.preventDefault();
      return false;
    }
  }
});

$('#sendButton').on('click', function (e) {
  var text = $('.usrInput').val();
  if (text == '' || $.trim(text) == '') {
    $('#userInput').focus();
    e.preventDefault();
    return false;
  } else {
    //destroy the existing chart

    if (typeof chatChart !== 'undefined') {
      chatChart.destroy();
    }
    $('.chart-container').remove();
    if (typeof modalChart !== 'undefined') {
      modalChart.destroy();
    }

    $('.suggestions').remove();
    $('#paginated_cards').remove();
    $('.quickReplies').remove();
    $('.usrInput').focus();
    setUserResponse(text);
    send(text);
    e.preventDefault();
    return false;
  }
});
$.fn.selectRange = function (start, end) {
  if (end === undefined) {
    end = start;
  }
  return this.each(function () {
    if ('selectionStart' in this) {
      this.selectionStart = start;
      this.selectionEnd = end;
    } else if (this.setSelectionRange) {
      this.setSelectionRange(start, end);
    } else if (this.createTextRange) {
      var range = this.createTextRange();
      range.collapse(true);
      range.moveEnd('character', end);
      range.moveStart('character', start);
      range.select();
    }
  });
};
//==================================== Set user response =====================================
function setUserResponse(message) {
  var UserResponse =
    '<img class="userAvatar" src=' +
    'https://chatbot-rgai3.inf.u-szeged.hu/img/userAvatar.jpg' +
    '><p class="userMsg">' +
    message.trim() +
    ' </p><div class="clearfix"></div>';
  $(UserResponse).appendTo('.chats').show('slow');

  $('.usrInput').val('');
  scrollToBottomOfResults();
  showBotTyping();
  $('.suggestions').remove();
}

//=========== Scroll to the bottom of the chats after new message has been added to chat ======
function scrollToBottomOfResults() {
  var terminalResultsDiv = document.getElementById('chats');
  terminalResultsDiv.scrollTop = terminalResultsDiv.scrollHeight;
}

//============== send the user message to rasa server =============================================
function send(message) {
  $.ajax({
    url: 'https://chatbot-rgai3.inf.u-szeged.hu/rasa/webhook',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ message: message.trim(), sender: user_id }),
    success: function (botResponse, status) {
      console.log('Response from Rasa: ', botResponse, '\nStatus: ', status);

      // if user wants to restart the chat and clear the existing chat contents
      if (message.toLowerCase() == '/restart') {
        $('#userInput').prop('disabled', false);

        //if you want the bot to start the conversation after restart
        action_trigger();
        return;
      }
      setBotResponse(botResponse);
    },
    error: function (xhr, textStatus, errorThrown) {
      if (message.toLowerCase() == '/restart') {
        // $("#userInput").prop('disabled', false);
        //if you want the bot to start the conversation after the restart action.
        // action_trigger();
        // return;
      }
      //console.log("url =" + document.location.protocol + " asd " + document.location.hostname);
      // if there is no response from rasa server
      setBotResponse('');
      console.log('Error from bot end: ', textStatus);
    }
  });
}

//=================== set bot response in the chats ===========================================
function setBotResponse(response) {
  //display bot response after 500 milliseconds
  setTimeout(function () {
    hideBotTyping();
    if (response.length < 1) {
      //if there is no response from Rasa, send  fallback message to the user
      // var fallbackMsg = 'I am facing some issues, please try again later!!!';
      // var BotResponse =
      //   '<img class="botAvatar" src="https://inf.u-szeged.hu/algmi/chatbot/img/botAvatar.png"/><p class="botMsg">' +
      //   fallbackMsg +
      //   '</p><div class="clearfix"></div>';
      // $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
      // scrollToBottomOfResults();
    } else {
      //if we get response from Rasa
      const res = [];
      for (i = 0; i < response.length; i++) {
        //check if the response contains "text"
        if (response[i].hasOwnProperty('text')) {
          var BotResponse =
            '<img class="botAvatar" src="https://chatbot-rgai3.inf.u-szeged.hu/img/botAvatar.png"/><p class="botMsg">' +
            response[i].text +
            '</p><div class="clearfix"></div>';
          $(BotResponse).appendTo('.chats').hide().fadeIn(1000);

          res.push(response[i].text);
        }
      }
      tts(res.join(' '));
    }
    scrollToBottomOfResults();
  }, 1000);
}

//====================================== Toggle chatbot =======================================
$('#profile_div').click(function () {
  $('.profile_div').toggle();
  $('.widget').toggle();
  $('.usrInput').focus();
});

//====================================== DropDown ==================================================
//render the dropdown messageand handle user selection
function renderDropDwon(data) {
  var options = '';
  for (i = 0; i < data.length; i++) {
    options +=
      '<option value="' + data[i].value + '">' + data[i].label + '</option>';
  }
  var select =
    '<div class="dropDownMsg"><select class="browser-default dropDownSelect"> <option value="" disabled selected>Choose your option</option>' +
    options +
    '</select></div>';
  $('.chats').append(select);

  //add event handler if user selects a option.
  $('select').change(function () {
    var value = '';
    var label = '';
    $('select option:selected').each(function () {
      label += $(this).text();
      value += $(this).val();
    });

    setUserResponse(label);
    send(value);
    $('.dropDownMsg').remove();
  });
}

//====================================== Suggestions ===========================================

function addSuggestion(textToAdd) {
  setTimeout(function () {
    var suggestions = textToAdd;
    var suggLength = textToAdd.length;
    $(
      ' <div class="singleCard"> <div class="suggestions"><div class="menu"></div></div></diV>'
    )
      .appendTo('.chats')
      .hide()
      .fadeIn(1000);
    // Loop through suggestions
    for (i = 0; i < suggLength; i++) {
      $(
        '<div class="menuChips" data-payload=\'' +
          suggestions[i].payload +
          "'>" +
          suggestions[i].title +
          '</div>'
      ).appendTo('.menu');
    }
    scrollToBottomOfResults();
  }, 1000);
}

// on click of suggestions, get the value and send to rasa
$(document).on('click', '.menu .menuChips', function () {
  var text = this.innerText;
  var payload = this.getAttribute('data-payload');
  console.log('payload: ', this.getAttribute('data-payload'));
  setUserResponse(text);
  send(payload);

  //delete the suggestions once user click on it
  $('.suggestions').remove();
});

//====================================== functions for drop-down menu of the bot  =========================================

//restart function to restart the conversation.
$('#restart').click(function () {
  restartConversation();
});

//clear function to clear the chat contents of the widget.
$('#clear').click(function () {
  $('.chats').fadeOut('normal', function () {
    $('.chats').html('');
    $('.chats').fadeIn();
  });
});

//close function to close the widget.
$('#close').click(function () {
  $('.profile_div').toggle();
  $('.widget').toggle();
  scrollToBottomOfResults();
});

//====================================== Cards Carousel =========================================

function showCardsCarousel(cardsToAdd) {
  var cards = createCardsCarousel(cardsToAdd);

  $(cards).appendTo('.chats').show();

  if (cardsToAdd.length <= 2) {
    $('.cards_scroller>div.carousel_cards:nth-of-type(' + i + ')').fadeIn(3000);
  } else {
    for (var i = 0; i < cardsToAdd.length; i++) {
      $('.cards_scroller>div.carousel_cards:nth-of-type(' + i + ')').fadeIn(
        3000
      );
    }
    $('.cards .arrow.prev').fadeIn('3000');
    $('.cards .arrow.next').fadeIn('3000');
  }

  scrollToBottomOfResults();

  const card = document.querySelector('#paginated_cards');
  const card_scroller = card.querySelector('.cards_scroller');
  var card_item_size = 225;

  card.querySelector('.arrow.next').addEventListener('click', scrollToNextPage);
  card.querySelector('.arrow.prev').addEventListener('click', scrollToPrevPage);

  // For paginated scrolling, simply scroll the card one item in the given
  // direction and let css scroll snaping handle the specific alignment.
  function scrollToNextPage() {
    card_scroller.scrollBy(card_item_size, 0);
  }
  function scrollToPrevPage() {
    card_scroller.scrollBy(-card_item_size, 0);
  }
}

function createCardsCarousel(cardsData) {
  var cards = '';

  for (i = 0; i < cardsData.length; i++) {
    title = cardsData[i].name;
    ratings = Math.round((cardsData[i].ratings / 5) * 100) + '%';
    data = cardsData[i];
    item =
      '<div class="carousel_cards in-left">' +
      '<img class="cardBackgroundImage" src="' +
      cardsData[i].image +
      '"><div class="cardFooter">' +
      '<span class="cardTitle" title="' +
      title +
      '">' +
      title +
      '</span> ' +
      '<div class="cardDescription">' +
      '<div class="stars-outer">' +
      '<div class="stars-inner" style="width:' +
      ratings +
      '" ></div>' +
      '</div>' +
      '</div>' +
      '</div>' +
      '</div>';

    cards += item;
  }

  var cardContents =
    '<div id="paginated_cards" class="cards"> <div class="cards_scroller">' +
    cards +
    '  <span class="arrow prev fa fa-chevron-circle-left "></span> <span class="arrow next fa fa-chevron-circle-right" ></span> </div> </div>';

  return cardContents;
}

//====================================== Quick Replies ==================================================

function showQuickReplies(quickRepliesData) {
  var chips = '';
  for (i = 0; i < quickRepliesData.length; i++) {
    var chip =
      '<div class="chip" data-payload=\'' +
      quickRepliesData[i].payload +
      "'>" +
      quickRepliesData[i].title +
      '</div>';
    chips += chip;
  }

  var quickReplies =
    '<div class="quickReplies">' + chips + '</div><div class="clearfix"></div>';
  $(quickReplies).appendTo('.chats').fadeIn(1000);
  scrollToBottomOfResults();
  const slider = document.querySelector('.quickReplies');
  let isDown = false;
  let startX;
  let scrollLeft;

  slider.addEventListener('mousedown', (e) => {
    isDown = true;
    slider.classList.add('active');
    startX = e.pageX - slider.offsetLeft;
    scrollLeft = slider.scrollLeft;
  });
  slider.addEventListener('mouseleave', () => {
    isDown = false;
    slider.classList.remove('active');
  });
  slider.addEventListener('mouseup', () => {
    isDown = false;
    slider.classList.remove('active');
  });
  slider.addEventListener('mousemove', (e) => {
    if (!isDown) return;
    e.preventDefault();
    const x = e.pageX - slider.offsetLeft;
    const walk = (x - startX) * 3; //scroll-fast
    slider.scrollLeft = scrollLeft - walk;
  });
}

// on click of quickreplies, get the value and send to rasa
$(document).on('click', '.quickReplies .chip', function () {
  var text = this.innerText;
  var payload = this.getAttribute('data-payload');
  console.log('chip payload: ', this.getAttribute('data-payload'));
  setUserResponse(text);
  send(payload);

  //delete the quickreplies
  $('.quickReplies').remove();
});

//====================================== Get User Location ==================================================
function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      getUserPosition,
      handleLocationAccessError
    );
  } else {
    response = 'Geolocation is not supported by this browser.';
  }
}

function getUserPosition(position) {
  response =
    'Latitude: ' +
    position.coords.latitude +
    ' Longitude: ' +
    position.coords.longitude;
  console.log('location: ', response);

  //here you add the intent which you want to trigger
  response =
    '/inform{"latitude":' +
    position.coords.latitude +
    ',"longitude":' +
    position.coords.longitude +
    '}';
  $('#userInput').prop('disabled', false);
  send(response);
  showBotTyping();
}

function handleLocationAccessError(error) {
  switch (error.code) {
    case error.PERMISSION_DENIED:
      console.log('User denied the request for Geolocation.');
      break;
    case error.POSITION_UNAVAILABLE:
      console.log('Location information is unavailable.');
      break;
    case error.TIMEOUT:
      console.log('The request to get user location timed out.');
      break;
    case error.UNKNOWN_ERROR:
      console.log('An unknown error occurred.');
      break;
  }

  response = '/inform{"user_location":"deny"}';
  send(response);
  showBotTyping();
  $('.usrInput').val('');
  $('#userInput').prop('disabled', false);
}

//======================================bot typing animation ======================================
function showBotTyping() {
  var botTyping =
    '<img class="botAvatar" id="botAvatar" src="https://chatbot-rgai3.inf.u-szeged.hu/img/botAvatar.png"/><div class="botTyping">' +
    '<div class="bounce1"></div>' +
    '<div class="bounce2"></div>' +
    '<div class="bounce3"></div>' +
    '</div>';
  $(botTyping).appendTo('.chats');
  $('.botTyping').show();
  scrollToBottomOfResults();
}

function hideBotTyping() {
  $('#botAvatar').remove();
  $('.botTyping').remove();
}

//====================================== Collapsible =========================================

// function to create collapsible,
// for more info refer:https://materializecss.com/collapsible.html
function createCollapsible(data) {
  //sample data format:
  //var data=[{"title":"abc","description":"xyz"},{"title":"pqr","description":"jkl"}]
  list = '';
  for (i = 0; i < data.length; i++) {
    item =
      '<li>' +
      '<div class="collapsible-header">' +
      data[i].title +
      '</div>' +
      '<div class="collapsible-body"><span>' +
      data[i].description +
      '</span></div>' +
      '</li>';
    list += item;
  }
  var contents = '<ul class="collapsible">' + list + '</uL>';
  $(contents).appendTo('.chats');

  // initialize the collapsible
  $('.collapsible').collapsible();
  scrollToBottomOfResults();
}

//====================================== creating Charts ======================================

//function to create the charts & render it to the canvas
function createChart(
  title,
  labels,
  backgroundColor,
  chartsData,
  chartType,
  displayLegend
) {
  //create the ".chart-container" div that will render the charts in canvas as required by charts.js,
  // for more info. refer: https://www.chartjs.org/docs/latest/getting-started/usage.html
  var html =
    '<div class="chart-container"> <span class="modal-trigger" id="expand" title="expand" href="#modal1"><i class="fa fa-external-link" aria-hidden="true"></i></span> <canvas id="chat-chart" ></canvas> </div> <div class="clearfix"></div>';
  $(html).appendTo('.chats');

  //create the context that will draw the charts over the canvas in the ".chart-container" div
  var ctx = $('#chat-chart');

  // Once you have the element or context, instantiate the chart-type by passing the configuration,
  //for more info. refer: https://www.chartjs.org/docs/latest/configuration/
  var data = {
    labels: labels,
    datasets: [
      {
        label: title,
        backgroundColor: backgroundColor,
        data: chartsData,
        fill: false
      }
    ]
  };
  var options = {
    title: {
      display: true,
      text: title
    },
    layout: {
      padding: {
        left: 5,
        right: 0,
        top: 0,
        bottom: 0
      }
    },
    legend: {
      display: displayLegend,
      position: 'right',
      labels: {
        boxWidth: 5,
        fontSize: 10
      }
    }
  };

  //draw the chart by passing the configuration
  chatChart = new Chart(ctx, {
    type: chartType,
    data: data,
    options: options
  });

  scrollToBottomOfResults();
}

// on click of expand button, get the chart data from gloabl variable & render it to modal
$(document).on('click', '#expand', function () {
  //the parameters are declared gloabally while we get the charts data from rasa.
  createChartinModal(
    title,
    labels,
    backgroundColor,
    chartsData,
    chartType,
    displayLegend
  );
});

//function to render the charts in the modal
function createChartinModal(
  title,
  labels,
  backgroundColor,
  chartsData,
  chartType,
  displayLegend
) {
  //if you want to display the charts in modal, make sure you have configured the modal in index.html
  //create the context that will draw the charts over the canvas in the "#modal-chart" div of the modal
  var ctx = $('#modal-chart');

  // Once you have the element or context, instantiate the chart-type by passing the configuration,
  //for more info. refer: https://www.chartjs.org/docs/latest/configuration/
  var data = {
    labels: labels,
    datasets: [
      {
        label: title,
        backgroundColor: backgroundColor,
        data: chartsData,
        fill: false
      }
    ]
  };
  var options = {
    title: {
      display: true,
      text: title
    },
    layout: {
      padding: {
        left: 5,
        right: 0,
        top: 0,
        bottom: 0
      }
    },
    legend: {
      display: displayLegend,
      position: 'right'
    }
  };

  modalChart = new Chart(ctx, {
    type: chartType,
    data: data,
    options: options
  });
}

//TTS stuff

function concat(arrays) {
  // sum of individual array lengths
  let totalLength = arrays.reduce((acc, value) => acc + value.length, 0);

  if (!arrays.length) return null;

  let result = new Uint8Array(totalLength);

  // for each array - copy it over result
  // next array is copied right after the previous one
  let length = 0;
  for (let array of arrays) {
    result.set(array, length);
    length += array.length;
  }

  return result;
}

const tts = (text) => {
  fetch(
    'https://chatbot-rgai3.inf.u-szeged.hu/flask/tts?' +
      new URLSearchParams({
        q: text
      })
  )
    .then(async (res) => {
      const reader = res.body.getReader();
      let result,
        data = [];
      while (!(result = await reader.read()).done) {
        data.push(result.value);
      }
      data = concat(data);
      return data;
    })
    .then((data) => {
      let blob = new Blob([data], { type: 'audio/wav' });
      let blobUrl = window.URL.createObjectURL(blob);
      if (window.audio !== undefined && !window.audio.paused){
        window.audio.pause();
	setTimeout(() => {}, 20);  
      }	    
      window.audio = new Audio(blobUrl);
      window.audio.controls = false;
      window.audio.play().catch((err) => {
        console.log(err);
      });
    });
};

/*
Speech2Text stuff
*/
const extract_text = (object) => {
  let message = JSON.stringify(object);
  return message.match('"(.*)"')[1];
};

function SpeechtexAsrHandler() {
  this.controlReceived = function (msg) {
    console.log('control');
    console.log('MSG: [' + msg.type + '] ' + msg.msg + ' (' + msg.params + ')');
  };
  this.errorReceived = function (msg) {
    console.log('error');
    console.log('MSG: [' + msg.type + '] ' + msg.msg + ' (' + msg.params + ')');
  };
  this.resultReceived = function (msg) {
    //Modify this
    const extracted_text = extract_text(msg.params);
    if (msg.msg === '0' && extracted_text.length < 2) {    
      document.getElementById('userInput').value = extracted_text;
    } else {
      if (extracted_text === '' || extracted_text.length < 2) return;
      setUserResponse(extracted_text);
      send(extracted_text);
    }
  };
}

function SpeechtexMessage(raw_msg) {
  this.type;
  this.msg;
  this.params = new Array();

  if (raw_msg.indexOf('|') > -1) {
    this.type = raw_msg.substring(0, raw_msg.indexOf('|'));
    if (raw_msg.indexOf(';') > -1) {
      this.msg = raw_msg.substring(
        raw_msg.indexOf('|') + 1,

        raw_msg.indexOf(';')
      );

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
  let fromWhere = '';
  const lab = document.getElementById('stt-connect');
  this.connect = function () {
    ws = new WebSocket(wsProxyUrl);
    ws.onopen = () => {
      document.getElementById('proxy-connect').innerText =
        ' Sikeres proxy kapcsolódás!';
    };
    ws.onerror = () => {
      document.getElementById('proxy-connect').innerText = ' Websocket hiba!';
    };

    this.init();
    ws.onmessage = function (e) {
      var msg = e.data;
      console.log(msg);
      // Sikeres ASR kapcsolodas
      if (msg == MSG_IN_BIND_OK) asrBindOk = true;
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
      // getModels
      else if (msg.startsWith('control|models')) {
        const regexp = /control\|models;general_hu,(\d),/;
        const available_models = msg.match(regexp);
        if (parseInt(available_models[1]) === 0) {
          lab.innerText =
            ' Jelenleg nincs további elérhető Speech to text szál.';
          lab.style.color = 'red';
        } else {
          lab.style.color = '9f9f9f';
          console.log(fromWhere);
          if (fromWhere === 'connect') {
            lab.innerText = ` Sikeres Speech to Text csatlakozás!`;
          } else {
            lab.innerText = ` Jelenleg ${available_models[1]} szál elérhető.`;
          }
        }
      }
      propagate(msg);
    };
  };
  this.setHandler = function (h) {
    handler = h;
  };
  propagate = function (msg) {
    var spMsg = new SpeechtexMessage(msg);
    if (
      !(handler == null) &&
      spMsg.type === 'error' &&
      typeof handler.errorReceived == 'function'
    )
      handler.errorReceived(spMsg);
    else if (
      !(handler == null) &&
      spMsg.type === 'result' &&
      typeof handler.resultReceived == 'function'
    )
      handler.resultReceived(spMsg);
    else if (
      !(handler == null) &&
      spMsg.type === 'control' &&
      typeof handler.controlReceived == 'function'
    )
      handler.controlReceived(spMsg);
  };
  this.init = function () {
    if (hasGetUserMedia()) {
      navigator.getUserMedia(
        { video: false, audio: true },
        function (localMediaStream) {
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
        },
        this.getUserMediaError
      );
    }
  };
  this.getUserMediaError = function (e) {};
  this.disconnect = function () {
    if (!(ws == null)) {
      ws.close();
      document.getElementById('proxy-connect').innerText =
        ' Sikeres proxy bontás!';
    } else {
      document.getElementById('proxy-connect').innerText =
        ' Nem volt a proxyhoz kapcsolódva!';
    }
  };
  const sendControl = function (control) {
    if (!(ws == null)) ws.send(control);
    else propagate('error|001;No connection to Speechtex ASR Proxy.');
  };
  const sendAudioData = function (data) {
    if (!data) return -1;
    var len = data.length,
      i = 0;
    var dataAsInt16Array = new Int16Array(len);
    while (i < len) dataAsInt16Array[i] = convert(data[i++]);

    if (!(ws == null)) ws.send(dataAsInt16Array);
    return 1;
  };
  /*
  Csatlakozas adott modellt futtato felismero csatornahoz
  */
  this.bindAsrChannel = function (model) {
    fromWhere = 'connect';
    sendControl(MSG_OUT_GET_MODELS);
    sendControl(MSG_OUT_DISCONNECT);
    sendControl(MSG_OUT_BIND_REQUEST + ';' + model);
  };
  /*
  Felismeres inditasa
  */
  this.startRecognition = function () {
    if (!asrBindOk) {
      return;
    }
    console.log(MSG_OUT_RECOG_START + ';' + sampleRate + ';' + loopbackId);
    sendControl(
      MSG_OUT_RECOG_START + ';' + sampleRate + ';' + loopbackId + ';0;'
    );
    console.log('asd');
    document.getElementById('recording').innerText =
      ' Hangfelismerés folyamatban.';

    recording = true;
  };
  this.stopRecognition = function () {
    sendControl(MSG_OUT_RECOG_STOP + ';');
    document.getElementById('recording').innerText =
      ' Hangfelismerés leállítva.';
    recording = false;
  };
  this.generateLoopback = function (dic) {
    var params = '';
    if (Array.isArray(dic)) {
      for (i = 0; i < dic.length; i++) {
        var dici = dic[i];
        if (Array.isArray(dici) && dici.length >= 2) {
          if (params !== '') params += ';';
          params += dici[0] + '=' + dici[1];
        }
      }
    }

    sendControl(MSG_OUT_CREATE_LOOPBACK + ';' + params);
  };
  this.getModels = function () {
    fromWhere = 'models';
    sendControl(MSG_OUT_GET_MODELS);
  };
}

/*
Egyeb szukseges metodusok
*/
navigator.getUserMedia =
  navigator.getUserMedia ||
  navigator.webkitGetUserMedia ||
  navigator.mozGetUserMedia;
function hasGetUserMedia() {
  return !!(
    navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mediaDevices.getUserMedia ||
    navigator.msGetUserMedia
  );
}
function convert(n) {
  var v = n * 32768;
  return Math.max(-32767, Math.min(32767, v));
}

var spAsrConn;

function connect(ws_addr) {
  spAsrConn = new SpeechtexAsrConnection(ws_addr);
  var handler = new SpeechtexAsrHandler();
  spAsrConn.setHandler(handler);
  spAsrConn.connect();
}
function disconnect() {
  spAsrConn.disconnect();
}
function bindAsrChannel(model) {
  spAsrConn.bindAsrChannel(model);
}
function startDictate() {
  spAsrConn.startRecognition();
}
function stopDictate() {
  spAsrConn.stopRecognition();
}
function uploadDic() {
  var dic = [
    ['Saab', 'száb'],
    ['Toyota', 'tojota'],
    ['Seat', 'szeát'],
    ['Mitsubishi', 'micubisi'],
    ['BMW', 'béemvé']
  ];

  spAsrConn.generateLoopback(dic);
}
function getModels() {
  spAsrConn.getModels();
}
