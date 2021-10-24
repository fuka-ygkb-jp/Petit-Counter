#!/usr/local/bin/perl
$ver = '2.3';     # 本プログラムのバージョン。変更しないで下さい。
#+------------------------------------------------------------------------
#|Petit-Count (ぷちカウンタ)                                    2016/08/12
#|(C)2000, 2016 不可思議絵の具(http://ygkb.jp/)
#+------------------------------------------------------------------------
# ☆☆☆ 設定項目 ☆☆☆
#+------------------------------------------------------------------------
# [ログファイルを格納したディレクトリの名前]
# ログ用ディレクトリは petit/ 配下に作って下さい。
$Dir_Log = 'log';

# [カウンタ用画像を格納したディレクトリの名前]
# カウンタ画像用ディレクトリは petit/ 配下に作って下さい。
$Dir_Img = 'image';

# [カウンタのイメージの名前 (標準で使用する物)]
$DigitName = 'fuksan';

# [カウントアップさせないIPアドレス]
# 必ずIPアドレスの形式で指定して下さい。
# ワイルドカードなどは使えません。　あくまで、おまけ的な物と考えて下さい。
$DenyIP = '192.168.0.30';

# [集計画面で最終アクセス者のIPアドレスを表示させるか]
# させる場合は 1 を。　させない場合は 0 を指定。
$DoPutLastIP = 1;

# [gifcat.plのありか (通常は変更しないで下さい)]
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
if (($ENV{'REMOTE_ADDR'} eq $LOG_IP)
	 || ($ENV{'REMOTE_ADDR'} eq $DenyIP)
	 || $OutputOnly)
{
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
	$ENV{'TZ'} = 'JST-9';
	$P{DIGIT} = 0;
	$OutputOnly = 0;	# 1=出力のみ

	### 現在時刻の取得
	$RUN_TIME = time;
	@RUN_TIME = localtime($RUN_TIME);
	$RUN_week = &Func_TotalWeek($RUN_TIME[7]);

	### 引数取得
	foreach $data (split(/&/, $ENV{'QUERY_STRING'})) {
		($key , $val) = split(/=/,$data);
		$val =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("C",hex($1))/ge;
		$val =~ tr/+/ /;
		$val =~ s/\t//g;
		$P{$key} = $val;
	}

	# 動作モード
	if ($P{MODE} =~ /^-([atyw])$/) {				# 頭に - があれば出力のみ
		$P{MODE} = $1;
		$OutputOnly = 1;
	} elsif ($P{MODE} !~ /^[atyw]$/) {				# 無ければ普通にチェック
		$P{MODE} = 'a';								# 満たさなければ強制的に a に
	}

	# 桁数
	if ($P{DIGIT} > 20) { &Macro_PutError('e0001'); }
	else { $P{DIGIT} -= 1; }

	# フォント名
	$DigitName = $P{FONT} if ($P{FONT} ne '');

	# ディレクトリ名を修正
	$Dir_Img = "./${Dir_Img}/${DigitName}/";		# フォント格納ディレクトリ
	$Dir_Log = "./${Dir_Log}/";						# ログ格納ディレクトリ

	### オプション指定がなければログ表示モード(ここで終わり)
	if ($ENV{'QUERY_STRING'} eq '') {
		require './ps.pl';
	}

	### 時刻表示モードだったらここで終わり
	if ($P{MODE} eq 'w') {
		print &Func_PutGIF(sprintf("%02dc%02d",$RUN_TIME[2],$RUN_TIME[1]));
		exit(0);
	}

	### ログを開く
	unless (open(LOG,"+<${Dir_Log}$P{LOG}.log")) { &Macro_PutError('e0000'); }
	flock(LOG,2);
	chop(@log = <LOG>);

	# 初めての記録なら初期化
	if ($log[0] eq '') {
		$log[0] = "PC2#${RUN_TIME}";									# ヘッダ
		$log[1] = "${RUN_TIME}#0#-";									# 各種情報
		$log[2] = "0#0#0#0#0#0#0#0";									# 日別集計
		$log[3] = "0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0";	# 時間別集計
		$log[4] = "0#0#0#0#0#0#0";										# 曜日別集計
		$log[5] = "0#0#0#0#0#0";										# 週別集計
		$log[6] = "0#0#0#0#0#0#0#0#0#0#0#0";							# 月別集計
		$log[7] = "0#0#0#0#0#0";										# 年度別集計
	}

	# 通常処理
	($LOG_VER, $LOG_SINCE) = split(/#/,$log[0]);
	if ($LOG_VER ne 'PC2') { &Macro_PutError('e1110'); }				# ログVer.不正→処理中止

	($LOG_TIME, $ALL, $LOG_IP) = split(/#/,$log[1]);
	@DAILY = split(/#/,$log[2]);
	@HOUR  = split(/#/,$log[3]);
	@YOUBI = split(/#/,$log[4]);
	@WEEK  = split(/#/,$log[5]);
	@MONTH = split(/#/,$log[6]);
	@YEAR  = split(/#/,$log[7]);

	# ログの日付を求める
	@LOG_TIME = localtime($LOG_TIME);
	$LOG_week = &Func_TotalWeek($LOG_TIME[7]);
}


### [カウントする]
sub Macro_Count {
	### 何日間経過したか求める
	$n = $RUN_TIME[7] - $LOG_TIME[7];
	$n += 366 if ($n < 0);			# 年が明けた場合補正(n+366日経過)

	if ($n == 0) { $DAILY[0]++; }	# 同じ日
	elsif ($n > 0) {				# n日経過
		for (1 .. $n) { unshift(@DAILY, 0); }
		$DAILY[0] = 1;
	}


	### 何週間経過したか求める
	$n = $RUN_week - $LOG_week;
	$n += 53 if ($n < 0);			# 年が明けた場合補正(n+53週間経過)

	if ($n == 0) { $WEEK[0]++; }	# 同じ週
	elsif ($n > 0) {				# n週間経過
		for (1 .. $n) { unshift(@WEEK, 0); }
		$WEEK[0] = 1;
	}


	### 何年間経過したか求める
	$n = $RUN_TIME[5] - $LOG_TIME[5];

	if (($n == 0) || ($n < 0)) { $YEAR[0]++; }	# 同じ年(サーバ側時計が古い場合もこの処理)
	elsif ($n > 0) {							# n年経過
		@MONTH = (0) x 12;						# 月別集計をreset
		for (1 .. $n) { unshift(@YEAR, 0); }
		$YEAR[0] = 1;
	}

	$ALL++;
	$HOUR[${RUN_TIME[2]}]++;
	$YOUBI[${RUN_TIME[6]}]++;
	$MONTH[${RUN_TIME[4]}]++;
}


### [ファイルに保存する]
sub Macro_SaveData {
	$log[0] = "PC2#${LOG_SINCE}";
	$log[1] = "${RUN_TIME}#${ALL}#$ENV{'REMOTE_ADDR'}";
	$log[2] = &Func_Array2Str(8,  *DAILY);					# 日別集計
	$log[3] = &Func_Array2Str(24, *HOUR);					# 時間別集計
	$log[4] = &Func_Array2Str(7,  *YOUBI);					# 曜日別集計
	$log[5] = &Func_Array2Str(6,  *WEEK);					# 週別集計
	$log[6] = &Func_Array2Str(12, *MONTH);					# 月別集計
	$log[7] = &Func_Array2Str(6,  *YEAR);					# 年度別集計

	seek(LOG,0,0);
	foreach $line (@log) { print LOG "$line\n"; }
	truncate(LOG,tell);

	flock(LOG,8);
	close(LOG);

	### 配列の内容を一行の文字列に直す関数
	### $limitより大きなデータは切り捨てる
	sub Func_Array2Str {
		local($limit, *array) = @_;
		splice(@array, $limit);
		return join("#", @array);
	}
}


### [出力する]
sub Macro_Output {
	if ($P{MODE} eq 'a')    { print &Func_PutGIF($ALL); }
	elsif ($P{MODE} eq 't') { print &Func_PutGIF($DAILY[0]); }
	elsif ($P{MODE} eq 'y') { print &Func_PutGIF($DAILY[1]); }
}


### [エラー出力]
sub Macro_PutError {
	local ($code) = @_;

	require "$gifcat";
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);

	# e0000 = ファイルオープン失敗
	# e0001 = 桁数あふれ
	# e1110 = ログのバージョンが不正
	for ($i=0 ; $i < length($code) ; $i++) {
		$n = substr($code, $i, 1);
		push(@Digit, "./${n}.gif");
	}
	print &gifcat'gifcat(@Digit);
	exit(1);
}


### [gifを出力]
sub Func_PutGIF {
	local($Data) = @_;
	local($i,$n,@array);

	require "$gifcat";
	print "Content-type: image/gif\n";
	print "Expires: 01/01/1970 00:00:00 JST\n\n";	# キャッシュを無効にする
	binmode(STDOUT);

	### 桁数を指定されたら、足りない分を0で補う
	$Data = ('0'x($P{DIGIT}-(length($Data)-1))).$Data if (length($Data)-1 < $P{DIGIT});

	for ($i=0 ; $i < length($Data) ; $i++) {
		$n = substr($Data, $i, 1);
		push(@array, "${Dir_Img}${n}${DigitName}.gif");
	}

	return &gifcat'gifcat(@array);
}


### 通算週を求める関数
sub Func_TotalWeek {
	local($total) = @_;
	local($week);

	if ($total < 7) { $week = 0; }	# 0除算対策
	else { $week = int($total/7); }

	return $week;
}
