#!/usr/local/bin/perl
$ver = '1.0';     # 本プログラムのバージョン。変更しないで下さい。
;#+------------------------------------------------------------------------
;#|Petit-Count (ぷちカウンタ)                                    2000/06/07
;#|(C)2000 不可思議絵の具(http://tech.millto.net/~fuka/)
;#+------------------------------------------------------------------------
;# ☆☆☆ 設定項目 ☆☆☆
;#+------------------------------------------------------------------------
;# [ログファイルを格納したディレクトリの名前]
;# ログ用ディレクトリは petit/ 配下に作って下さい。
$Dir_Log = 'log';

;# [カウンタ用画像を格納したディレクトリの名前]
;# カウンタ画像用ディレクトリは petit/ 配下に作って下さい。
$Dir_Img = 'image';

;# [カウンタのイメージの名前(標準で使用する物)]
$DigitName = 'fuksan';

;# [gifcat.plの在処]　※通常は変更しないで下さい※
$gifcat = './gifcat.pl';


#+------------------------------------------------------------------------
# (設定ここまで)
#+------------------------------------------------------------------------
# ※ここからは分かる人だけ弄って下さい。
# 　(タブのサイズ・[4]、折返し・[無し]で綺麗に表示されます)
#+------------------------------------------------------------------------
#|&main
#+------------------------------------------------------------------------
&Macro_Setup;
if ($ENV{'REMOTE_ADDR'} eq $ip) {		# 重複アクセスは記録しない
	&Macro_Output;
} else {
	&Macro_Count;
	&Macro_SaveData;
	&Macro_Output;
}
exit(0);


#+------------------------------------------------------------------------
#|プログラムの流れとしてのサブルーチン
#+------------------------------------------------------------------------
### 各種初期化
sub Macro_Setup {
	$Digit = 0;
	$ENV{'TZ'} = 'JST-9';

	### 現在時刻の取得
	($sec,$min,$hour,$day,$month,$year,$youbi,$total) = localtime(time);
	@table_youbi = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');
	$RUN_DATE = sprintf("%4d/%02d/%02d(%s)",1900+$year,$month+1,$day,$table_youbi[$youbi]);
	$RUN_TIME = sprintf("%02d:%02d:%02d",$hour,$min,$sec);

	### 引数取得
	foreach $data (split(/&/, $ENV{'QUERY_STRING'})) {
		($key , $val) = split(/=/,$data);
		$P{$key} = $val;
	}

	# ログファイル名
	$filename = $P{LOG};

	# 動作モード
	if    ($P{MODE} eq 'a') { $OutMode = 'a'; }		# 総カウント
	elsif ($P{MODE} eq 't') { $OutMode = 't'; }		# 本日カウント
	elsif ($P{MODE} eq 'y') { $OutMode = 'y'; }		# 昨日カウント
	elsif ($P{MODE} eq 'w') { $OutMode = 'w'; }		# 時刻表示
	else                    { $OutMode = 'a'; }		# それ以外

	# 桁数
	if ($P{DIGIT} > 9) { &Macro_PutError('e0001'); }
	else               { $Digit = $P{DIGIT}-1; }

	# フォント名
	$DigitName = $P{FONT} if ($P{FONT} ne '');

	### ディレクトリ名を修正
	$Dir_Img = "./${Dir_Img}/${DigitName}/";		# フォント格納ディレクトリ
	$Dir_Log = "./$Dir_Log/";						# ログ格納ディレクトリ

	### オプション指定がなければログ表示モード(ここで終わり)
	if ($ENV{'QUERY_STRING'} eq '') {
		require './ps.pl';
	}

	### 時刻表示モードだったらここで終わり
	if ($OutMode eq 'w') {
		$RUN_TIME = sprintf("%02dc%02d",$hour,$min);
		$Digit = 0;
		print &Func_PutGIF($RUN_TIME);
		exit(0);
	}

	### ログを開く
	unless (open(LOG,"+<${Dir_Log}${filename}.log")) { &Macro_PutError('e0000'); }
	flock(LOG,2);
	chop($line = <LOG>);
	$line = "${RUN_DATE}#${RUN_TIME}#0#0#0#" if ($line eq '');				#初めての記録なら初期化

	($date,$time,$all,$today,$yesterday,$ip) = split(/#/,$line);
}


### [カウントする]
sub Macro_Count {
	$all++;
	if($RUN_DATE ne $date) {
		$yesterday = $today;
		$today = 1;
	} else { $today++; }
}


### [ファイルに保存する]
sub Macro_SaveData {
	seek(LOG,0,0);
	print LOG "${RUN_DATE}#${RUN_TIME}#${all}#${today}#${yesterday}#$ENV{'REMOTE_ADDR'}\n";
	truncate(LOG,tell);
	flock(LOG,8);
	close(LOG);
}


### [出力する]
sub Macro_Output {
	if ($OutMode eq 'a')    { print &Func_PutGIF($all); }
	elsif ($OutMode eq 't') { print &Func_PutGIF($today); }
	elsif ($OutMode eq 'y') { print &Func_PutGIF($yesterday); }
}


### [gifを出力]
sub Func_PutGIF {
	local($Data) = @_;
	local($i,$n,@array);

	require "$gifcat";
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);

	### 桁数を指定されたら、足りない分を0で補う
	$Data = ('0'x($Digit-(length($Data)-1))).$Data if (length($Data)-1 < $Digit);

	for ($i=0 ; $i < length($Data) ; $i++) {
		$n = substr($Data, $i, 1);
		push(@array, "${Dir_Img}${n}${DigitName}.gif");
	}

	return &gifcat'gifcat(@array);
}


### [エラー出力]
sub Macro_PutError {
	local ($code) = @_;

	require "$gifcat";
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);

	# e0000 = ファイルオープン失敗
	# e0001 = 桁数あふれ
	# e1111 = 無効なオプション
	for ($i=0 ; $i < length($code) ; $i++) {
		$n = substr($code, $i, 1);
		push(@Digit, "./${n}.gif");
	}
	print &gifcat'gifcat(@Digit);
	exit(1);
}
