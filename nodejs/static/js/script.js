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
    url: 'https://www.inf.u-szeged.hu/algmi/chatbot/mongo',
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
  setTimeout(function () {
    hideBotTyping();
    var msg =
      'Jó napot! Főnök Úr virtuális személyi asszisztense vagyok, én kezelem a naptárában az időpont foglalásokat. Mikorra szeretne hozzá időpontot?';
    var BotResponse =
      '<img class="botAvatar" src="https://inf.u-szeged.hu/algmi/chatbot/img/botAvatar.png"/><p class="botMsg">' +
      msg +
      '</p><div class="clearfix"></div>';
    $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
    scrollToBottomOfResults();
  }, 500);
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
    'https://inf.u-szeged.hu/algmi/chatbot/img/userAvatar.jpg' +
    '><p class="userMsg">' +
    message +
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
    url: 'https://inf.u-szeged.hu/algmi/chatbot/rasa/webhook',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({ message: message, sender: user_id }),
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
      var fallbackMsg = 'I am facing some issues, please try again later!!!';

      var BotResponse =
        '<img class="botAvatar" src="https://inf.u-szeged.hu/algmi/chatbot/img/botAvatar.png"/><p class="botMsg">' +
        fallbackMsg +
        '</p><div class="clearfix"></div>';

      $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
      scrollToBottomOfResults();
    } else {
      //if we get response from Rasa
      for (i = 0; i < response.length; i++) {
        //check if the response contains "text"
        if (response[i].hasOwnProperty('text')) {
          var BotResponse =
            '<img class="botAvatar" src="https://inf.u-szeged.hu/algmi/chatbot/img/botAvatar.png"/><p class="botMsg">' +
            response[i].text +
            '</p><div class="clearfix"></div>';
          $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
        }

        //check if the response contains "images"
        if (response[i].hasOwnProperty('image')) {
          var BotResponse =
            '<div class="singleCard">' +
            '<img class="imgcard" src="' +
            response[i].image +
            '">' +
            '</div><div class="clearfix">';
          $(BotResponse).appendTo('.chats').hide().fadeIn(1000);
        }
      }
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
  scrollToBottomOfResults();
});

//======================================bot typing animation ======================================
function showBotTyping() {
  var botTyping =
    '<img class="botAvatar" id="botAvatar" src="https://inf.u-szeged.hu/algmi/chatbot/img/botAvatar.png"/><div class="botTyping">' +
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
