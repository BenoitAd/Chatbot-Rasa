/**
 * scroll to the bottom of the chats after new message has been added to chat
 */
const converter = new showdown.Converter();
function scrollToBottomOfResults() {
  const terminalResultsDiv = document.getElementById("chats");
  terminalResultsDiv.scrollTop = terminalResultsDiv.scrollHeight;
}

/**
 * Set user response on the chat screen
 * @param {String} message user message
 */
function setUserResponse(message) {
  const user_response = `<img class="userAvatar" src='./static/img/userAvatar.jpg'><p class="userMsg">${message} </p><div class="clearfix"></div>`;
  $(user_response).appendTo(".chats").show("slow");

  $(".usrInput").val("");
  scrollToBottomOfResults();
  showBotTyping();
  $(".suggestions").remove();
}

/**
 * returns formatted bot response
 * @param {String} text bot message response's text
 *
 */
function getBotResponse(text) {
  botResponse = `<img class="botAvatar" src="./static/img/sara_avatar.png"/><span class="botMsg">${text}</span><div class="clearfix"></div>`;
  return botResponse;
}

/**
 * Renders bot response onto the chat screen
 * @param {Array} response - JSON array containing different types of bot response
 *
 * For more info: `https://rasa.com/docs/rasa/connectors/your-own-website#request-and-response-format`
 */
function setBotResponse(response) {
  // Renders bot response after 500 milliseconds
  setTimeout(() => {
    hideBotTyping();
    if (response.length < 1) {
      // If there is no response from Rasa, send a fallback message to the user
      const fallbackMsg = "I am facing some issues, please try again later!!!";
      const BotResponse = `<img class="botAvatar" src="./static/img/sara_avatar.png"/><p class="botMsg">${fallbackMsg}</p><div class="clearfix"></div>`;
      $(BotResponse).appendTo(".chats").hide().fadeIn(1000);
      scrollToBottomOfResults();
    } else {
      // If we get a response from Rasa
      response.forEach((res) => {
        let botResponse;
        if (res.text) {
          let html = converter.makeHtml(res.text);
          html = html.replaceAll("<p>", "").replaceAll("</p>", "").replaceAll("<strong>", "<b>").replaceAll("</strong>", "</b>");
          html = html.replace(/(?:\r\n|\r|\n)/g, "<br>");
          console.log(html);
          
          if (html.includes("<blockquote>")) {
            html = html.replaceAll("<br>", "");
            botResponse = getBotResponse(html);
          } else if (html.includes("<img")) {
            html = html.replaceAll("<img", '<img class="imgcard_mrkdwn" ');
            botResponse = getBotResponse(html);
          } else if (html.includes("<pre") || html.includes("<code>")) {
            botResponse = getBotResponse(html);
          } else if (html.includes("<ul") || html.includes("<ol") || html.includes("<li") || html.includes("<h3")) {
            html = html.replaceAll("<br>", "");
            botResponse = getBotResponse(html);
          } else {
            botResponse = `<img class="botAvatar" src="./static/img/sara_avatar.png"/><p class="botMsg">${res.text}</p><div class="clearfix"></div>`;
          }

          $(botResponse).appendTo(".chats").hide().fadeIn(1000);
        }

        if (res.image) {
          const imageResponse = `<div class="singleCard"><img class="imgcard" src="${res.image}"></div><div class="clearfix">`;
          $(imageResponse).appendTo(".chats").hide().fadeIn(1000);
        }

        if (res.buttons) {
          if (res.buttons.length > 0) {
            addSuggestion(res.buttons);
          }
        }

        if (res.attachment) {
          if (res.attachment.type === "video") {
            const videoResponse = `<div class="video-container"> <iframe src="${res.attachment.payload.src}" frameborder="0" allowfullscreen></iframe> </div>`;
            $(videoResponse).appendTo(".chats").hide().fadeIn(1000);
          }
        }

        if (res.custom) {
          const { payload } = res.custom;
          switch (payload) {
            case "quickReplies":
              showQuickReplies(res.custom.data);
              return;
            case "pdf_attachment":
              renderPdfAttachment(res);
              return;
            case "dropDown":
              renderDropDwon(res.custom.data);
              return;
            case "location":
              $("#userInput").prop("disabled", true);
              getLocation();
              scrollToBottomOfResults();
              return;
            case "cardsCarousel":
              showCardsCarousel(res.custom.data);
              return;
            case "chart":
              const { title, labels, backgroundColor, chartsData, chartType, displayLegend } = res.custom.data;
              createChart(title, labels, backgroundColor, chartsData, chartType, displayLegend);
              $(document).on("click", "#expand", () => {
                createChartinModal(title, labels, backgroundColor, chartsData, chartType, displayLegend);
              });
              return;
            case "collapsible":
              createCollapsible(res.custom.data);
              return;
          }
        }
      });
      scrollToBottomOfResults();
    }
    $(".usrInput").focus();
  }, 500);
}


/**
 * Sends the user message to the Rasa server.
 * @param {String} message - User message
 */
async function send(message) {
  // Optionally remove the artificial delay
  // await new Promise((r) => setTimeout(r, 2000)); 

  $.ajax({
    url: rasa_server_url,
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({ message, sender: sender_id }),
    success(botResponse, status) {
      console.log("Response from Rasa: ", botResponse, "\nStatus: ", status);

      // Ensure input is enabled after the response
      $("#userInput").prop("disabled", false);

      // Handle the /restart intent
      if (message.toLowerCase() === "/restart") {
        // Uncomment if you want the bot to start the conversation after restart
        // customActionTrigger();
        return;
      }

      setBotResponse(botResponse);
    },
    error(xhr, textStatus) {
      // Ensure input is enabled after an error
      $("#userInput").prop("disabled", false);

      // Handle the /restart intent
      if (message.toLowerCase() === "/restart") {
        // Uncomment if you want the bot to start the conversation after the restart action.
        // actionTrigger();
        return;
      }

      // Set error bot response
      setBotResponse("");
      console.log("Error from bot end: ", textStatus);
    },
  });
}

/**
 * Triggers an action in Rasa 1.x to start the conversation by greeting the user.
 */
function actionTrigger() {
  $.ajax({
    url: `http://localhost:5005/conversations/${sender_id}/execute`,
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      name: action_name,
      policy: "MappingPolicy",
      confidence: "0.98",
    }),
    success(botResponse, status) {
      console.log("Response from Rasa: ", botResponse, "\nStatus: ", status);

      if (Object.hasOwnProperty.call(botResponse, "messages")) {
        setBotResponse(botResponse.messages);
      }
      $("#userInput").prop("disabled", false);
    },
    error(xhr, textStatus) {
      setBotResponse("");
      console.log("Error from bot end: ", textStatus);
      $("#userInput").prop("disabled", false);
    },
  });
}


/**
 * Triggers a custom action in Rasa 2.x to start the conversation by greeting the user.
 */
function customActionTrigger() {
  $.ajax({
    url: "http://localhost:5055/webhook/",
    type: "POST",
    contentType: "application/json",
    data: JSON.stringify({
      next_action: action_name,
      tracker: {
        sender_id,
      },
    }),
    success(botResponse, status) {
      console.log("Response from Rasa: ", botResponse, "\nStatus: ", status);

      if (Object.hasOwnProperty.call(botResponse, "responses")) {
        setBotResponse(botResponse.responses);
      }
      $("#userInput").prop("disabled", false);
    },
    error(xhr, textStatus) {
      setBotResponse("");
      console.log("Error from bot end: ", textStatus);
      $("#userInput").prop("disabled", false);
    },
  });
}

/**
 * clears the conversation from the chat screen
 * & sends the `/resart` event to the Rasa server
 */
function restartConversation() {
  $("#userInput").prop("disabled", true);
  // destroy the existing chart
  $(".collapsible").remove();

  if (typeof chatChart !== "undefined") {
    chatChart.destroy();
  }

  $(".chart-container").remove();
  if (typeof modalChart !== "undefined") {
    modalChart.destroy();
  }
  $(".chats").html("");
  $(".usrInput").val("");
  send("/restart");
}
// triggers restartConversation function.
$("#restart").click(() => {
  restartConversation();
});

/**
 * if user hits enter or send button
 * */
$(".usrInput").on("keyup keypress", (e) => {
  const keyCode = e.keyCode || e.which;

  const text = $(".usrInput").val();
  if (keyCode === 13) {
    if (text === "" || $.trim(text) === "") {
      e.preventDefault();
      return false;
    }
    // destroy the existing chart, if yu are not using charts, then comment the below lines
    $(".collapsible").remove();
    $(".dropDownMsg").remove();
    if (typeof chatChart !== "undefined") {
      chatChart.destroy();
    }

    $(".chart-container").remove();
    if (typeof modalChart !== "undefined") {
      modalChart.destroy();
    }

    $("#paginated_cards").remove();
    $(".suggestions").remove();
    $(".quickReplies").remove();
    $(".usrInput").blur();
    setUserResponse(text);
    send(text);
    e.preventDefault();
    return false;
  }
  return true;
});

$("#sendButton").on("click", (e) => {
  const text = $(".usrInput").val();
  if (text === "" || $.trim(text) === "") {
    e.preventDefault();
    return false;
  }
  // destroy the existing chart
  if (typeof chatChart !== "undefined") {
    chatChart.destroy();
  }

  $(".chart-container").remove();
  if (typeof modalChart !== "undefined") {
    modalChart.destroy();
  }

  $(".suggestions").remove();
  $("#paginated_cards").remove();
  $(".quickReplies").remove();
  $(".usrInput").blur();
  $(".dropDownMsg").remove();
  setUserResponse(text);
  send(text);
  e.preventDefault();
  return false;
});
