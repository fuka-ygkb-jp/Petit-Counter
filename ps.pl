#!/usr/local/bin/perl
;#+------------------------------------------------------------------------
;#|Petit-Stat (ぷちカウンタ用アドイン：ぷちすたっと)             2000/06/07
;#|(C)2000 不可思議絵の具(http://tech.millto.net/~fuka/)
;#+------------------------------------------------------------------------
opendir(DIR, "$Dir_Log");
unless (-e $Dir_Log) { closedir(DIR); &Func_PutError("指定されたディレクトリ ($Dir_Log) が見つかりません。"); }
unless (-r $Dir_Log) { closedir(DIR); &Func_PutError("指定されたディレクトリ ($Dir_Log) を開くことが出来ませんでした。<BR>パーミッションが 705又は755 になっているか確認して下さい。"); exit(1); }
@filename = readdir(DIR);
closedir(DIR);
@filename = sort({$a cmp $b} @filename);

### ファイルリスト一覧から不適合ファイルを取り去る
### 対象 : ディレクトリ([.] [..]) / 拡張子が.logでない物
for ($i=0 ; $i < $#filename+1 ; $i++) {
	if (($filename[$i] eq '.') || ($filename[$i] eq '..') || ($filename[$i] =~ /.[^lL][^oO][^gG]$/)) {
		splice(@filename,$i,1); $i--;
	} else {
		$filename[$i] =~ s/.[lL][oO][gG]$//i;				# 拡張子を取り去る
	}
}

for ($i=0 ; $i < $#filename+1 ; $i++) {
	if ($filename[$i] eq '') { next; }

	### ファイルをオープン　エラーがあれば関数 Func_PutError へ
	unless (open(LOG,"<${Dir_Log}${filename[$i]}.log")) {
		&Func_PutError("ログファイル ( ${Dir_Log}${filename[$i]}.log ) を開くことが出来ませんでした。<BR>そのファイルは本当に存在していますか？<BR>パーミッションは適正 (606又は666) ですか？");
	}
	flock(LOG,1);
	chop($line = <LOG>);
	($date,$time,$all,$today,$yesterday,$ip) = split(/#/, $line);

	push(@LOG, "$filename[$i]#$line");												# 全体
	push(@RANK_A, sprintf("%06d:%s", $all, $filename[$i])) if ($all);				# 総合
	push(@RANK_T, sprintf("%06d:%s", $today, $filename[$i])) if ($today);			# 本日
	push(@RANK_Y, sprintf("%06d:%s", $yesterday, $filename[$i])) if ($yesterday);	# 昨日

	flock(LOG,8);
	close(LOG);
}

@RANK_A = sort({$b cmp $a} @RANK_A);
@RANK_T = sort({$b cmp $a} @RANK_T);
@RANK_Y = sort({$b cmp $a} @RANK_Y);


&html_head;

print "<TABLE border=1 cellspacing=0 cellpadding=1>";
print "<TR><TH>ページ</TH><TH>最終更新日時</TH><TH>最終記録IP</TH><TH>総合</TH><TH>本日</TH><TH>昨日</TH></TR>";
$SUM_all = $SUM_today = $SUM_yesterday = 0;
foreach $line (@LOG) {
	($logname, $date,$time,$all,$today,$yesterday,$ip) = split(/#/, $line);
	$SUM_all += $all;
	$SUM_today += $today;
	$SUM_yesterday += $yesterday;
	print "<TR align=right><TH>$logname</TH><TD>$date $time</TD><TD>$ip</TD><TD>$all</TD><TD>$today</TD><TD>$yesterday</TD></TR>";
}
print "<TR align=right><TH>サイト計</TH><TD>　</TD><TD>　</TD><TD>$SUM_all</TD><TD>$SUM_today</TD><TD>$SUM_yesterday</TD></TR>";
print "</TABLE>\n<BR>\n";

print "<TABLE border=0 cellspacing=0 cellpadding=0><TR><TD valign=top>\n";
&Macro_PutTable('総合', $SUM_all, @RANK_A);
print "</TD><TD valign=top>\n";
&Macro_PutTable('本日', $SUM_today, @RANK_T);
print "</TD><TD valign=top>\n";
&Macro_PutTable('昨日', $SUM_yesterday, @RANK_Y);
print "</TD></TR></TABLE>\n";

&html_tail;
exit(0);


sub Macro_PutTable {
	local($title, $total, @array) = @_;

	print "<TABLE border=1 cellspacing=0 cellpadding=1>";
	print "<TR><TH colspan=3>$titleランキング<BR>サイト計 : $total</TH></TR>";
	$i = 1;
	$ave = 0;
	foreach $line (@array) {
		($n, $data) = ($line =~ /^(\d\d\d\d\d\d):(.*)/);
		$ave_old = $ave;
		$n = int($n);
		$ave = sprintf("%2.1f",($n*100)/$total) if ($total);
		$width = int($ave);
		if ($ave eq $ave_old) {
			print "<TR><TD>　</TD><TD align=right>$data</TD><TD><IMG src=b.gif height=10 width=$width> $n</TD></TR>";
		} else {
			print "<TR><TD>${i}位</TD><TD align=right>$data</TD><TD><IMG src=b.gif height=10 width=$width> $n (${ave}%)</TD></TR>";
			$i++;
		}
	}
	print "</TABLE>\n";
}


### [エラー出力]
sub Func_PutError {
	local($mesg) = @_;
	$html_title = 'Error!';
	&html_head;
	print "<CENTER><P><B>[Error]</B>$mesg</P></CENTER>\n";
	&html_tail;
	exit(1);
}


;### HTML 頭の部分
sub html_head {
print <<"END";
Content-type: text/html

<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\">
<HTML>
<HEAD>
	<META http-equiv=\"Content-Type\" content=\"text/html; charset=Shift_JIS\">
	<META http-equiv=\"Content-Style-Type\" content=\"text/css\">
	<TITLE>ぷちカウンタ</TITLE>
	<STYLE type=\"text/css\"><!--
		BODY    {font-family:Arial,Verdana}
		A       {text-decoration:none; font-weight:bold}
		A:hover {text-decoration: underline}
	--></STYLE>
</HEAD>

<BODY bgcolor=#ffffff text=#7e2828 link=#7726c8 alink=#5c4fff vlink=#ff5959>

<B><FONT size=+1>ぷちカウンタ $ver</FONT></B>
<HR>

END
}


;### HTML しっぽの部分
sub html_tail {
	print "\n<HR>\n<DIV align=right><A href=\"http://tech.millto.net/~fuka/\">[Petit-Counter $ver] / &copy;2000 Enogu Fukashigi\@YugenKoubou</A></DIV>\n</BODY>\n</HTML>\n";
}
