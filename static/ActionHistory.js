class HistoryHandler{

    constructor(){

        this.history = [{"move" : "initial"}];
        this.now_clicked_id = "ActionButton_0";

        this.only_move_id = [];

        this.update_view();

    }

    update_view(){

        this.only_move_id = [];

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
                this.only_move_id.push(button_id);  // 移動アクションのリストに加える
            }
            else{

                // メッセージアクションがあったら
                if (keys.indexOf("message") >= 0){
                    var button_text = "message";
                }
                // fly_toがあったら
                else if (keys.indexOf("fly_to") >= 0){
                    var button_text = "fly_to : " + String(action["fly_to"]);
                    this.only_move_id.push(button_id);  // 移動アクションのリストに加える
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
                var el = "#TextAction_text_box";
                if (message_keys.indexOf("text") >= 0){
                    $(el).val(message_action["text"]);
                }else{$(el).val("");}

                // ライトアップ
                var el = "#LightUpAction_buttons p";
                if (message_keys.indexOf("light_up") >= 0){
                    $(el).text(message_action["light_up"].join(","));
                }else{$(el).val("");}

                // マーク
                var el = "#MarkAction_buttons p"
                if (message_keys.indexOf("mark") >= 0){
                    $(el).text(message_action["mark"].join(","));
                }else{$(el).val("");}
            }

            // そうじゃなかったら全て空白
            else{
                action_view_null();
            }
        }

    }

    add_action(action) {
        
        let now_touched_number = Number(this.now_clicked_id.split("_")[1]);


        // actionをhistoryのどこに付け加えるか //


        // もし今参照しているアクションが最新だったら
        if (now_touched_number == this.history.length-1){
            this.history.push(action);
        }
        // 最新でなかったら
        else{
            // moveだったら
            if (Object.keys(action).indexOf("move") >= 0){
                window.alert("kora!");
                exit;
            }
            // message
            else if (Object.keys(action).indexOf("message") >= 0){
                // 現在参照しているアクションの後ろに追加
                this.history.splice(now_touched_number+1, 0, action);
            }
            // fly_to
            else if (Object.keys(action).indexOf("fly_to") >= 0){
                this.history.push(action);
            }
        }


        // ユーザがどこを参照しているようにするのか //

        if (Object.keys(action).indexOf("fly_to") >= 0){
            // fly_toなら最新のを参照する
            this.now_clicked_id = "ActionButton_" + String(this.history.length-1);
        }
        else{
            // 付け加えたやつを参照 : 今参照しているアクションの下に付け加えるので、idは必ず以下のようになる
            this.now_clicked_id = "ActionButton_" + String(now_touched_number+1);
        }
        


        // todo もしmove or fly_toだったら、pythonの履歴に追加してもらう（現在は後ろに追加するのみ）
        if ((Object.keys(action).indexOf("move") >= 0) || (Object.keys(action).indexOf("fly_to") >= 0)){

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

        let latest_PushAction_id = get_latest_PushorFlyToAction_id(this.id);
        let latest_PushAction_order = History.only_move_id.indexOf(latest_PushAction_id);

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



// メッセージアクションをヒストリーに追加

$(document).on("click", "#AddAction", function(){

    let text = $("#TextAction_text_box").val();
    let LightUp_pos = $("#" + "LightUpAction_buttons p").text().split(",");
    let Mark_pos = $("#" + "MarkAction_buttons p").text().split(",");

    let action = {"message" : {}};

    if (text != null){
        action["message"]["text"] = text;
    }
    if (LightUp_pos.length > 0){
        action["message"]["light_up"] = LightUp_pos;
    }
    if (Mark_pos.length > 0){
        action["message"]["mark"] = Mark_pos;
    }

    History.add_action(action);
})


// fly_toアクションを追加

// pythonのBOARDを現在見ているのと同じ盤面に -> History.add_action

$(document).on("click", "#add_FlyTo", function(){

    let the_clicked_id = History.now_clicked_id;
    let move_order = Number(History.only_move_id.indexOf(the_clicked_id));

    // 現在参照しているのがmessageだったらエラーを出す
    if (Object.keys(History.history[Number(the_clicked_id.split("_")[1])]).indexOf("message") > 0){
        window.alert("メッセージのところにfly_toは追加できません");
        exit;
    }

    $.ajax(
        {
        url : "/fly_to/" + move_order,
        type : 'GET',
        })
        .done(function(no_data){
            console.log("pushed to python the fly_to");

            // 盤面を反映
            Board.get_board_from_server();

            // historyに加えて、history画面も更新
            let action = {"fly_to" : move_order};
            History.add_action(action);

        })
        .fail(function(jqXHR, textStatus, errorThrown){
            console.log("failed fly_to");
        });
})


// todo
function action_view_null(){
    $("#TextAction_text_box").val("");
    $("#LightUpAction_buttons p").text("");
    $("#MarkAction_buttons p").text("");
}


// アクションを足すボタンを押した時
$(document).on("click", ".one_action_add_button", function(){
    Board.now_is_adding_action = !Board.now_is_adding_action;
    if (Board.now_is_adding_action){
        $(".OneSquare").css("background-color", "gold");
        let adding_action_kind = this.id.split("_")[1];
        Board.now_is_adding_kind = adding_action_kind;
    }
    else{
        $(".OneSquare").css("background-color", Board.default_color);
    }
})


// アクションを消すボタンを押した時
$(document).on("click", "#DelAction", function(){

    let watching_id = History.now_clicked_id;
    let watching_number = Number(watching_id.split("_")[1]);
    let watching_action = History.history[watching_number];

    if (watching_number == 0){
        window.alert("０番目は消去できません");
        exit;
    }


    // もしmove or fly_toだったら、
    // それが最新じゃなかったら以降も削除
    // 移動オンリーのリストから消して、python側も削除

    if ((Object.keys(watching_action).indexOf("move") >= 0) || (Object.keys(watching_action).indexOf("fly_to") >= 0)){

        // historyリストからそれ以降を削除
        History.history = History.history.slice(0, watching_number);

        // only_moveからそれ以降を削除
        let move_order = History.only_move_id.indexOf(watching_id);
        History.only_move_id = History.only_move_id.slice(0, move_order);

        // pytyhon側の移動アクションからそれ以降を削除
        $.ajax(
            {
            url : "/update_board_history/" + String(move_order),
            type : 'GET',
            })
            .done(function(no_data){
                console.log("success pushed to python update_BOARD_HISTORY");
            })
            .fail(function(jqXHR, textStatus, errorThrown){
                console.log("failed update BOARD_HISTORY");
            });
        
    }

    // メッセージだったら
    else if (Object.keys(watching_action).indexOf("message") >= 0){
        // historyリストからそれを削除
        History.history.splice(watching_number, 1);
    }

    else{
        window.alert("oioi");
    }

    // 画面を更新
    History.now_clicked_id = "ActionButton_" + String(watching_number - 1);
    History.update_view();

    // 盤面を更新
    Board.draw_main_board();

})



// 指定したidから遡って、一番最近（遅い）moveアクションもしくはfly_toアクションを探してidを返す
function get_latest_PushorFlyToAction_id(action_id){
    
    let id_number = Number(action_id.split("_")[1]);
    let action = History.history[id_number];

    if ((Object.keys(action).indexOf("move") >= 0) || (Object.keys(action).indexOf("fly_to") >= 0)){
        return action_id;
    }
    else{
        return get_latest_PushorFlyToAction_id(action_id.split("_")[0] + "_" + String(id_number-1));
    }

}

