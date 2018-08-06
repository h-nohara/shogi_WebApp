class HistoryHandler{

    constructor(){

        this.history = [{"move" : "initial"}];
        this.now_clicked_id = "ActionButton_0";

        this.only_action_id = [];

        this.update_view();

    }

    update_view(){

        this.only_action_id = [];

        $("#history_scroll").empty();  // 子要素を全て削除
        var parent = document.getElementById("history_scroll");

        // タイトルボタンを作成
        let title_button = make_HistoryTitle_button();
        parent.appendChild(title_button);

        for (let i=0; i<this.history.length; i++){

            let action = this.history[i];
            let button_id = "ActionButton_" + String(i);  // idは順番通りに


            // 中身を確認して表示テキストを決める

            let keys = Object.keys(action);

            // もし移動だったら
            if (keys.indexOf("move") >= 0){
                var button_text = action["move"];
                this.only_action_id.push(button_id);  // アクションのリストに加える
            }
            else{

                // メッセージアクションがあったら
                if (keys.indexOf("message") >= 0){
                    var button_text = "message";
                }
            }

            // アクションボタンを作成
            let btn = make_OneAction_button(button_text, button_id);
            parent.appendChild(btn);

        }

        // 現在見ているアクションの背景色を変化
        $("#"+this.now_clicked_id).css("background-color", "gold");


        // 現在見ているアクションがメッセージだったら、その内容各項を代入する

        //todo
        if (this.now_clicked_id != null){

            let now_touched_number = Number(this.now_clicked_id.split("_")[1]);
            let now_watching_action = this.history[now_touched_number];

            // メッセージだったら各要素代入
            if (Object.keys(now_watching_action).indexOf("message") >= 0){

                let message_action = now_watching_action["message"];
                let message_keys = Object.keys(message_action);

                // テキスト
                if (message_keys.indexOf("text") >= 0){
                    $("#TextAction_text_box").val(message_action["text"]);
                }else{$("#TextAction_text_box").val("");}

                // ライトアップ

                // マーク
            }

            // そうじゃなかったら全て空白
            else{
                action_view_null();
            }
        }

    }

    add_action(action) {
        
        let now_touched_number = Number(this.now_clicked_id.split("_")[1]);

        // もし今参照しているアクションが最新だったら
        if (now_touched_number == this.history.length-1){
            this.history.push(action);
        }
        // 最新でなかったら
        else{
            // 駒の移動だったら
            if (Object.keys(action).indexOf("move") >= 0){
                window.alert("kora!");
            }
            // 駒の移動以外
            else{
                // 現在参照しているアクションの後ろに追加
                this.history.splice(now_touched_number+1, 0, action);
            }
        }

        // 付け加えたやつを参照 : 今参照しているアクションの下に付け加えるので、idは必ず以下のようになる
        this.now_clicked_id = "ActionButton_" + String(now_touched_number+1);
        


        // todo もしmove（盤面）だったら、pythonの履歴に追加してもらう（現在は後ろに追加するのみ）
        if (Object.keys(action).indexOf("move") >= 0){

            $.ajax({
                url : "/memorize_board_history",
                type : "GET"
            })
            .done(function(no_data){
                console.log("pushed to python memorize");
            })
            .fail(function(jqXHR, textStatus, errorThrown){
                console.log("oh my");
            })
        }
        
        // 更新したhistoryを元に画面を更新
        this.update_view();
    }
}


function make_HistoryTitle_button(){

    let title_button = document.createElement("button");
    title_button.innerHTML = "アクション履歴";
    title_button.style.backgroundColor = "black";
    title_button.style.color = "white";
    title_button.style.width = "100%"
    title_button.style.height = "10vh";

    return title_button;
}

function make_OneAction_button(button_text, button_id){

    let btn = document.createElement("button");
    btn.innerHTML = button_text;
    btn.id = button_id;
    btn.className = "OneAction";
    btn.style.backgroundColor = "white";
    btn.style.color = "black";
    // btn.style.fontSize = "180%";
    btn.style.width = "100%";
    btn.style.height = "10vh";

    return btn;
}


$(document).on("click", ".OneAction", function(){

    console.log("ActionButton clicked");
    console.log(History.now_clicked_id);
    console.log(this.id);

    if (History.now_clicked_id != this.id){

        // 現在見ているアクションを更新
        History.now_clicked_id = this.id;

        // python側のBOARDをここ場面にする

        let latest_PushAction_id = get_latest_PushAction_id(this.id);
        let latest_PushAction_order = History.only_action_id.indexOf(latest_PushAction_id);

        $.ajax(
            {
            url : "/fly_to/" + latest_PushAction_order,
            type : 'GET',
            })
            .done(function(no_data){
                console.log("pushed to python the fly_to");

                // 盤面を反映
                Board.get_board_from_server();

                // 画面をアップデート
                History.update_view();

            })
            .fail(function(jqXHR, textStatus, errorThrown){
                console.log("failed fly_to");
            });

    }

})


// todo

$(document).on("click", "#AddAction", function(){

    let text = $("#TextAction_text_box").val();

    let action = {"message" : {}};

    if (text != null){
        action["message"]["text"] = text;
    }

    // ライトアップ
    // マーク

    History.add_action(action);
})


// todo
function action_view_null(){
    console.log(")))))))))))))))))))))))))))))");
    $("#TextAction_text_box").val("");
    // ライトアップ
    // マーク
}


// 指定したidから遡って、一番最近（遅い）moveアクションを探してidを返す
function get_latest_PushAction_id(action_id){
    
    let id_number = Number(action_id.split("_")[1]);
    let action = History.history[id_number];

    if (Object.keys(action).indexOf("move") >= 0){
        return action_id;
    }
    else{
        return get_latest_PushAction_id(action_id.split("_")[0] + "_" + String(id_number-1));
    }

}