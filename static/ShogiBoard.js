var PieceNames_normal_NotNari = ["HI", "KA", "KI", "GI", "KE", "KY", "FU"];
var PieceName_normal2kanji = {
    "OU" : "王",
    "HI" : "飛",
    "KA" : "角",
    "KI" : "金",
    "GI" : "銀",
    "KE" : "桂",
    "KY" : "香",
    "FU" : "歩",
    "RY" : "龍",
    "UM" : "馬",
    "NG" : "成銀",
    "NK" : "成桂",
    "NY" : "成香",
    "TO" : "と"
};


function DictKeys_to_String(dict){

    console.log("transforming");

    let new_dict = {};

    for (key in dict){
        key_string = key.toString();
        new_dict[key_string] = dict[key];
    }

    return new_dict;
}


class ShogiBoard {

    constructor(){

        console.log("constructer start");

        this.main_sub_LocPiece = "def";
        this.LocPieceDict_main = {};
        this.LocPieceDict_sub = {};

        this.default_color = "antiquewhite";

        // ターン
        this.is_sente = true;
        
        // ユーザの操作の現在
        this.now_is_touched = false;
        this.now_touched_loc = null;
        this.now_legal_moves = [];


        // アクションを足している最中かどうか
        this.now_is_adding_action = false;
        this.now_is_adding_kind = null;  // "LightUp" or "Mark"


        // 初期配置を描画
        this.draw_main_board_base();
        this.draw_sub_board_base();

        this.draw_main_board();
    }

    walk(){
        window.alert("walk");
    }


    // ユーザの操作の現在をリセット

    init_state_now(){
        
        this.now_is_touched = false;
        this.now_touched_loc = null;
        this.now_legal_moves = [];
    }

    // todo
    reset(){
        pass;
    }


    
    // pythonから盤面の状況を辞書で取得して反映
    draw_main_board(){
        this.get_board_from_server();
    }

    draw_main_board_kouhan(){

        console.log("kouhan");
        console.log(this.main_sub_LocPiece);

        this.LocPieceDict_main = DictKeys_to_String(this.main_sub_LocPiece["main"]);

        console.log("transofrmed!");
        console.log(this.LocPieceDict_main);

        for (let key in this.LocPieceDict_main){
            let piece_str = this.LocPieceDict_main[key];
            if (piece_str != null){
                $("#"+key).text(piece_str);
            }
            else{
                $("#"+key).text("");
            }
        
        }

        // サブボードを更新
        this.draw_sub_board_kouhan();
    }

    draw_sub_board_kouhan(){
        console.log("start draw sub_board");
        this.LocPieceDict_sub = this.main_sub_LocPiece["sub"];
        console.log(this.LocPieceDict_sub);
        console.log("blank");

        for (let i=0; i<2; i++){

            if (i == 0){
                var PieceDict = this.LocPieceDict_sub["sente"];
            }
            else{
                var PieceDict = this.LocPieceDict_sub["gote"];
            }

            for (let PieceName in PieceDict){
                let the_id = "#"+PieceName+String(i);
                let the_text = PieceName_normal2kanji[PieceName]+":"+PieceDict[PieceName];
                $(the_id).text(the_text);
            }
        }
    }

    // メインボードのベースを描画
    draw_main_board_base(){
        for (var loc_y=1; loc_y<=9; loc_y++){
            for (var x=1; x<=9; x++){
                var loc_x = 10 - x;
                var btn = document.createElement("button");
                var Loc = String(loc_x) + String(loc_y);
                // btn.innerHTML = Loc;
                btn.id = Loc;
                btn.className = "OneSquare";
                btn.style.backgroundColor = this.default_color;
                btn.style.color = "black";
                btn.style.fontSize = "120%";
                document.getElementById("main_board").appendChild(btn);
            }
        }

        console.log("base drawed");
    }

    // サブボードのベースを描画
    draw_sub_board_base(){

        // 手駒のidは "HI0"　のような形式（０：先手、１：後手）
        for (let i=0; i<2; i++){

            if (i==0){var sente_or_gote = "sente";} else{var sente_or_gote = "gote";}

            // let PieceDict = this.LocPieceDict_sub[i];
            for (let PieceName of PieceNames_normal_NotNari){
                let btn = document.createElement("button");
                btn.id = PieceName + String(i);
                btn.innerHTML = PieceName;
                btn.className = "PieceInHand";
                btn.style.backgroundColor = this.default_color;
                btn.style.color = "black";
                btn.style.fontSize = "180%";
                document.getElementById("sub_board_" + sente_or_gote).appendChild(btn);
            }
        }
    }

    // draw_sub_board_base(){

    // }

    child_clicked(Loc){

        // もしアクションを足している最中だったら

        if (this.now_is_adding_action){

            let el = "#" + this.now_is_adding_kind + "Action_buttons";
            let before_text = $(el + " p").text();

            if (before_text != ""){before_text += ",";}
            let after_text = before_text + Loc;
            $(el + " p").text(after_text);
        }

        // そうでなく、普通の駒の操作だったら

        else{

            console.log("now legal moves was");
            console.log(this.now_legal_moves);
            console.log("clicked :" + Loc);

            // 事前に駒がクリックされていた時
            if (this.now_is_touched){

                console.log("year, was touched");

                // 移動可能な場所がクリックされたら
                if ((this.now_legal_moves.indexOf(Loc) >= 0) || (this.now_legal_moves.indexOf(Loc + "+") >= 0)){

                    console.log("I can move there!");

                    // 成るか成らないか選べる時は選択ウィンドウを出し、その後の処理はウィンドウウィジェット側で行う
                    if ((this.now_legal_moves.indexOf(Loc) >= 0) && (this.now_legal_moves.indexOf(Loc+"+") >= 0)){

                        this.check_nari(this.now_touched_loc, Loc);
                    }

                    // 選べない時
                    else{

                        // 成れない時は自動でそのまま

                        // 必ず成らなければいけない時
                        if ((this.now_legal_moves.indexOf(Loc) == -1) && (this.now_legal_moves.indexOf(Loc+"+") >= 0)){
                            Loc = Loc + "+";
                        }

                        // todo
                        this.push_and_reflect_and_init_user_state(this.now_touched_loc, Loc);
                    }
                }

                // 移動可能でない場所がクリックされたら
                else {

                    console.log("oh , I cant move there");
                    
                    // 背景を元に戻す
                    $(".OneSquare").css("background-color", this.default_color);

                    // ユーザの操作状況を反映
                    this.now_touched_loc = Loc;

                    // todo
                    this.draw_legal_moves(Loc);
                }
            }


            // どこもクリックされていなかった時

            else{

                console.log("not touched");
                
                // ユーザの操作状況を反映
                this.now_is_touched = true;
                this.now_touched_loc = Loc;
                this.draw_legal_moves(Loc);
            }

        }

    }


    // pythonから盤面の状況を辞書で取得
    get_board_from_server(){

        $.ajax(
            {
              url:'/get_board',
              type:'GET',
            //   data: JSON.stringify(Loc),
            //   dataType: 'json',
            //   contentType: 'application/json'
            })
            .done(function(data, textStatus, jqXHR ){
                    console.log("got board from python");
                    console.log(data);
                    Board.main_sub_LocPiece = data;
                    Board.draw_main_board_kouhan();
                  })
            .fail(function(jqXHR, textStatus, errorThrown){
                    console.log("failed function get_boatd_from_server");
            });;
        
    }


    // 移動可能な場所をpythonから取得して描画

    // todo
    draw_legal_moves(Loc){

        function after_get(){

            console.log("start draw legal_moves");
            console.log(Board.now_legal_moves);

            for (var dest of Board.now_legal_moves){
                $("#"+dest[0]+dest[1]).css("background-color", "gold");
            };
        }

        this.get_legal_moves_from_server(Loc, after_get);
    }


    // pythonからlegal_movesを取得
    get_legal_moves_from_server(Loc, after_get_func){

        console.log("test");
        console.log(Loc);

        // todo

        $.ajax(
            {
              url:'/get_legal_moves/'+Loc,
              type:'POST',
              data: JSON.stringify(Loc),
            //   dataType: 'json',
            //   contentType: 'application/json'
            })
            .done(function(legal_moves){

                    console.log("received legal moves from python");
                    console.log(legal_moves);

                    if (legal_moves == ""){
                        Board.now_legal_moves = [];
                    }
                    else{
                        Board.now_legal_moves = legal_moves.split(",");
                    }

                    after_get_func();

                  })
            .fail(function(jqXHR, textStatus, errorThrown){
                    console.log("failed");
                  });;
    }

    push_and_reflect_and_init_user_state(start_loc, destination_loc){

        $.ajax(
            {
              url:'/push/'+start_loc+"/"+destination_loc,
              type:'GET',
            //   data: JSON.stringify(Loc),
            //   dataType: 'json',
            //   contentType: 'application/json'
            })
            .done(function(data){
                console.log("pushed to python");
                // 表示等を操作
                Board.main_sub_LocPiece = data;
                Board.push_and_reflect_and_init_user_state_kouhan();

                // ヒストリーに反映
                let action = {"move" : start_loc+destination_loc}
                History.add_action(action);
            })
            .fail(function(jqXHR, textStatus, errorThrown){
                console.log("failed");
            });
    }

    push_and_reflect_and_init_user_state_kouhan(){

        // 盤面を表示に反映
        this.draw_main_board_kouhan();

        // ユーザの状態を元に戻す
        this.init_state_now();
        // 背景を元に戻す
        $(".OneSquare").css("background-color", this.default_color);

        // ターンを交代
        if (this.is_sente){
            this.is_sente = false;
        }
        else{
            this.is_sente = true;
        }
    }

    check_nari(start_loc, dest_loc){

        if (confirm("成りますか？")) {
            dest_loc = dest_loc + "+";
        }
        
        this.push_and_reflect_and_init_user_state(start_loc, dest_loc);
    }

}




// 駒がタッチされたら
$(document).on("click", ".OneSquare", function(){
    let Loc = this.id;
    Board.child_clicked(Loc);
});

$(document).on("click", ".PieceInHand", function(){
    console.log("clicked tegoma");
    if (((this.id[2] == "0") && Board.is_sente) || ((this.id[2] == "1") && (!Board.is_sente))){
        let Loc = this.id[0]+ this.id[1];
        Board.child_clicked(Loc);
    }
})
