#!/usr/local/bin/perl
;#+------------------------------------------------------------------------
;#|Petit-Stat (�Ղ��J�E���^�p�A�h�C���F�Ղ���������)             2000/06/07
;#|(C)2000 �s�v�c�G�̋�(http://yugen.main.jp/)
;#+------------------------------------------------------------------------

### �����ݒ�
$ver .= '[en]';
$color0 = 'bgcolor=#b0b0b8';	# �\��
$color1 = 'bgcolor=#f0f0f8';	# �Z��
$color2 = 'bgcolor=#d0d0d8';	# ����
$color3 = 'bgcolor=#b0b0b8';	# ����(����)
$color4 = 'bgcolor=#b0b0c0';	# ����


@RUN_TIME = localtime(time);
$RUN_TIME = &Func_MakeDate(time);


### �t�@�C���̈ꗗ�𓾂�
opendir(DIR, "$Dir_Log");
unless (-e $Dir_Log) { closedir(DIR); &Func_PutError("Can't find directory ($Dir_Log) !!<BR>it's a correct name?"); }
unless (-r $Dir_Log) { closedir(DIR); &Func_PutError("Can't open directory ($Dir_Log) !!<BR>please check permission of directory."); }
@filename = readdir(DIR);
closedir(DIR);
@filename = sort({$a cmp $b} @filename);

# �t�@�C�����X�g�ꗗ����s�K���t�@�C������苎��
# �Ώ� : �f�B���N�g��([.] [..]) / �g���q��.log�łȂ���
for ($i=0 ; $i < $#filename+1 ; $i++) {
	if ($filename[$i] eq '.'
		 || $filename[$i] eq '..'
		 || $filename[$i] !~ /.[lL][oO][gG]$/)
	{
		splice(@filename,$i,1); $i--;
	} else {
		$filename[$i] =~ s/.log$//i;				# �g���q����苎��
	}
}


### ���O��ǂ݂Ƃ�A���v�𓾂�
foreach $filename (@filename) {
	unless (open(LOG,"<${Dir_Log}${filename}.log")) {
		push(@LOG, "<S>${filename}</S>(Can't read)#-#-#-#-");		# ����
		next;
	}
	flock(LOG,1);
	chop(@log = <LOG>);

	($LOG_VER, $LOG_SINCE) = split(/#/,$log[0]);
	if ($LOG_VER ne 'PC2') {
		push(@LOG, "<S>${filename}</S>(Illegal log)#-#-#-#-");		# ����
		next;
	}
	
	($LOG_TIME, $ALL, $LOG_IP) = split(/#/,$log[1]);
	($TODAY, $YESTERDAY) = split(/#/,$log[2]);
	$WEEK = (split(/#/,$log[5]))[0];
	$MONTH = (split(/#/,$log[6]))[$RUN_TIME[4]];

	### ���O�T�v
	push(@LOG, "$filename#$ALL#$LOG_TIME#$LOG_SINCE#$LOG_IP");

	### �����L���O
	push(@RANK_A, "$ALL:$filename") if ($ALL);						# ����
	push(@RANK_M, "$MONTH:$filename") if ($MONTH);					# ����
	push(@RANK_W, "$WEEK:$filename") if ($WEEK);					# �T��
	push(@RANK_T, "$TODAY:$filename") if ($TODAY);					# �{��
	push(@RANK_Y, "$YESTERDAY:$filename") if ($YESTERDAY);			# ���

	### �����L���O�p�̑��v���o���Ă���
	$SUM_all += $ALL;
	$SUM_month += $MONTH;
	$SUM_week += $WEEK;
	$SUM_today += $TODAY;
	$SUM_yesterday += $YESTERDAY;

	### �J�E���g
	push(@DAILY, "$filename:$log[2]");
	push(@HOUR,  "$filename:$log[3]");
	push(@YOUBI, "$filename:$log[4]");
	push(@WEEK,  "$filename:$log[5]");
	push(@MONTH, "$filename:$log[6]");
	push(@YEAR,  "$filename:$log[7]");

	flock(LOG,8);
	close(LOG);
}

### �\�[�g
@RANK_A = sort({$b <=> $a} @RANK_A);
@RANK_M = sort({$b <=> $a} @RANK_M);
@RANK_W = sort({$b <=> $a} @RANK_W);
@RANK_T = sort({$b <=> $a} @RANK_T);
@RANK_Y = sort({$b <=> $a} @RANK_Y);

&html_head;

print "<CENTER>\n";

### ���O�̏��
print "<TABLE border=0 cellspacing=2 cellpadding=1>";
print "<TR $color0><TH colspan=5>Logfile status report</TH></TR>";
print "<TR $color2><TH>Title</TH><TH>Total</TH><TH>Last accessed</TH><TH>Since</TH><TH>Last logged IP</TH></TR>";
foreach $line (@LOG) {
	($filename, $all, $log_time, $log_since, $log_ip) = split(/#/, $line);
	$log_since = &Func_MakeDate($log_since) if ($log_since ne '-');
	$log_time = &Func_MakeDate($log_time) if ($log_time ne '-');

	print "<TR align=right $color1><TH $color2>$filename</TH><TD>$all</TD><TD>$log_time</TD><TD>$log_since</TD>";
	if ($DoPutLastIP) { print "<TD>$log_ip</TD>"; }
	else { print "<TD>.</TD>"; }
	print "</TR>";
}
print "<TR align=right $color2><TH>Site total</TH><TD>$SUM_all</TD><TD>.</TD><TD>.</TD><TD>.</TD></TR>";
print "</TABLE>\n";

print "\n<HR>\n\n";

### �J�E���g�W�v�\
&Macro_PutTable(*DAILY, 0, 'Daily Report');
print "<BR>\n";
&Macro_PutTable(*WEEK,  1, 'Weekly Report');
print "<BR>\n";
&Macro_PutTable(*MONTH, 2, 'Monthly Report');
print "<BR>\n";
&Macro_PutTable(*YEAR,  3, 'Yearly Report');
print "<BR>\n";
&Macro_PutTable(*YOUBI, 4, 'Daily Summary');
print "<BR>\n";
&Macro_PutTable(*HOUR,  5, 'Hourly Summary');

print "\n<HR>\n\n";

### �����L���O
print "<TABLE border=0 cellspacing=0 cellpadding=0><TR valign=top><TD>\n\t";
&Macro_PutTable_Rank('Total', $SUM_all, *RANK_A);
print "</TD><TD>\n\t";
&Macro_PutTable_Rank('Today\'s', $SUM_today, *RANK_T);
print "</TD><TD>\n\t";
&Macro_PutTable_Rank('Yesterday\'s', $SUM_yesterday, *RANK_Y);
print "</TD></TR></TABLE>\n";

print "\n<BR>\n\n";

print "<TABLE border=0 cellspacing=0 cellpadding=0><TR valign=top><TD>\n\t";
&Macro_PutTable_Rank('This Month\'s', $SUM_month, *RANK_M);
print "</TD><TD>\n\t";
&Macro_PutTable_Rank('This Week\'s', $SUM_week, *RANK_W);
print "</TD></TR></TABLE>\n";
print "</CENTER>\n";


&html_tail;
exit(0);

sub Macro_PutTable {
	local(*ARRAY, $unit, $title) = @_;
	local($filename, $data, @array, @TBL, @sum, $log, $line);

	$TBL[0] = 'today,yesterday,2days(ago),3days,4days,5days,6days,7days';
	$TBL[1] = 'this week,last week,2weeks(ago),3weeks,4weeks,5weeks';
	$TBL[2] = 'Jan,Feb,Mar,Apr,May,Jun,Jul,Aug,Sep,Oct,Nov,Dec';
	$TBL[3] = 'this year, last year,2years(ago),3years,4years,5years';
	$TBL[4] = 'Sun,Mon,Tue,Wed,Thu,Fri,Sat';
	$TBL[5] = '0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23';

	@unit = split(/,/, $TBL[$unit]);
	$max = $#unit + 4;

	# �\��
	print "<TABLE border=0 cellspacing=2 cellpadding=1>";
	print "<TR $color0><TH colspan=$max>$title</TH></TR>";

	# ����
	print "<TR $color2><TH>Title</TH>";
	for ($i=0 ; $i < $#unit+1 ; $i++) { print "<TH>$unit[$i]</TH>"; }
	print "<TH>Total</TH><TH $color4>Ave.</TH></TR>";

	# ���e
	foreach $line (@ARRAY) {
		$sum = 0;

		($filename, $log) = split(/:/, $line);
		@array = split(/#/, $log);

		# ���ʂ̕���
		print "<TR $color1 align=right><TH $color2>$filename</TH>";
		for ($i=0 ; $i < $#array+1 ; $i++) {
			print "<TD>$array[$i]</TD>";
			$sum[$i] += $array[$i];
		}

		# �y�[�W���v�ƕ��ϒl
		$SUM_page = &Func_CalcSum(@array);
		printf("<TH $color2>%d</TH><TH $color4>%0.1f</TH>",$SUM_page,$SUM_page/($#array+1));
		print "</TR>";
	}

	# �T�C�g���v�ƕ��ϒl
	print "<TR $color2 align=right><TH $color2>Total</TH>";
		foreach $n (@sum) { print "<TH>$n</TH>"; }
		$SUM_site = &Func_CalcSum(@sum);
		printf("<TH $color3>%d</TH><TH $color4>%0.1f</TH>",$SUM_site, $SUM_site/($#array+1));
		print "</TR>";
	print "</TABLE>\n";

	### ���R���̓������z�����荞�ނƍ��v�l��Ԃ��֐�
	sub Func_CalcSum {
		local(@a) = @_;
		local($s, $n);
		foreach $n (@a) { $s += $n; }
		return $s;
	}
}


sub Macro_PutTable_Rank {
	local($title, $total, *array) = @_;
	local($i, $ave) = 0;

	print "<TABLE border=0 cellspacing=2 cellpadding=1>";
	print "<TR $color0><TH colspan=3>$title ranking<BR><FONT size=-1>Site total : $total</FONT></TH></TR>";
	foreach $line (@array) {
		($n,$data) = split(/:/, $line);
		$ave_old = $ave;
		$ave = sprintf("%2.1f",($n*100)/$total) if ($total);
		$width = int($ave);
		$width = 1 if ($width < 1);
		if ($ave eq $ave_old) {
			print "<TR $color1><TD $color3>.</TD><TH $color2 align=right>$data</TH><TD><IMG src=b.gif height=10 width=$width> $n</TD></TR>";
		} else {
			$i++;
			print "<TR $color1><TH $color3>${i}</TH><TH $color2 align=right>$data</TH><TD><IMG src=b.gif height=10 width=$width> $n (${ave}%)</TD></TR>";
		}
	}
	print "</TABLE>\n";
}


;### �ʎZ�b��������𓾂�֐�
;### (�ʎZ�b(1970/01/01 00:00:00����)����荞�ނ�[�N/��/��/(�j) ��:��:�b]�̕�����ɐ��`���ĕԂ�)
sub Func_MakeDate {
	local($t) = @_;
	local($sec, $min, $hour, $day, $month, $year, $youbi, @table_youbi);
	@table_youbi = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');
	($sec,$min,$hour,$day,$month,$year,$youbi,$total) = localtime($t);
	return sprintf("%4d/%02d/%02d(%s) %02d:%02d:%02d",1900+$year,$month+1,$day,$table_youbi[$youbi],$hour,$min,$sec);
}


;### [�G���[�o��]
sub Func_PutError {
	local($mesg) = @_;
	$html_title = 'Error!';
	&html_head;
	print "<CENTER><P><B>[Error]</B>$mesg</P></CENTER>\n";
	&html_tail;
	exit(1);
}


;### HTML ���̕���
sub html_head {
print <<"END";
Content-type: text/html

<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\">
<HTML>
<HEAD>
	<META http-equiv=\"Content-Type\" content=\"text/html; charset=iso-8859-1\">
	<META http-equiv=\"Content-Style-Type\" content=\"text/css\">
	<META name=\"GENERATOR\" content=\"Petit-Stat $ver\">
	<TITLE>Petit-Counter</TITLE>
	<STYLE type=\"text/css\"><!--
		BODY    {font-family:Arial,Verdana}
		A       {text-decoration:none; font-weight:bold}
		A:hover {text-decoration: underline}
	--></STYLE>
</HEAD>

<BODY bgcolor=#ffffff text=#000000 link=#7726c8 alink=#5c4fff vlink=#ff5959>

<TABLE width=100% border=0 cellpadding=0 cellspacing=0><TR valign=bottom>
	<TD><B><I><FONT size=+2>Petit-Counter $ver</FONT></I></B></TD>
	<TD align=right><B><I>$RUN_TIME</I></B></TD>
</TR></TABLE>

<HR>

END
}


;### HTML �����ۂ̕���
sub html_tail {
	print "\n<HR>\n<DIV align=right><A href=\"http://yugen.main.jp/\">[Petit-Counter $ver] / &copy;2000 Enogu Fukashigi\@YugenKoubou</A></DIV>\n</BODY>\n</HTML>\n";
}
