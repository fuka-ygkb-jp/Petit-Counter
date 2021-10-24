#!/usr/local/bin/perl
;#+------------------------------------------------------------------------
;#|Petit-Stat (�Ղ��J�E���^�p�A�h�C���F�Ղ���������)             2000/06/07
;#|(C)2000 �s�v�c�G�̋�(http://tech.millto.net/~fuka/)
;#+------------------------------------------------------------------------
opendir(DIR, "$Dir_Log");
unless (-e $Dir_Log) { closedir(DIR); &Func_PutError("�w�肳�ꂽ�f�B���N�g�� ($Dir_Log) ��������܂���B"); }
unless (-r $Dir_Log) { closedir(DIR); &Func_PutError("�w�肳�ꂽ�f�B���N�g�� ($Dir_Log) ���J�����Ƃ��o���܂���ł����B<BR>�p�[�~�b�V������ 705����755 �ɂȂ��Ă��邩�m�F���ĉ������B"); exit(1); }
@filename = readdir(DIR);
closedir(DIR);
@filename = sort({$a cmp $b} @filename);

### �t�@�C�����X�g�ꗗ����s�K���t�@�C������苎��
### �Ώ� : �f�B���N�g��([.] [..]) / �g���q��.log�łȂ���
for ($i=0 ; $i < $#filename+1 ; $i++) {
	if (($filename[$i] eq '.') || ($filename[$i] eq '..') || ($filename[$i] =~ /.[^lL][^oO][^gG]$/)) {
		splice(@filename,$i,1); $i--;
	} else {
		$filename[$i] =~ s/.[lL][oO][gG]$//i;				# �g���q����苎��
	}
}

for ($i=0 ; $i < $#filename+1 ; $i++) {
	if ($filename[$i] eq '') { next; }

	### �t�@�C�����I�[�v���@�G���[������Ί֐� Func_PutError ��
	unless (open(LOG,"<${Dir_Log}${filename[$i]}.log")) {
		&Func_PutError("���O�t�@�C�� ( ${Dir_Log}${filename[$i]}.log ) ���J�����Ƃ��o���܂���ł����B<BR>���̃t�@�C���͖{���ɑ��݂��Ă��܂����H<BR>�p�[�~�b�V�����͓K�� (606����666) �ł����H");
	}
	flock(LOG,1);
	chop($line = <LOG>);
	($date,$time,$all,$today,$yesterday,$ip) = split(/#/, $line);

	push(@LOG, "$filename[$i]#$line");												# �S��
	push(@RANK_A, sprintf("%06d:%s", $all, $filename[$i])) if ($all);				# ����
	push(@RANK_T, sprintf("%06d:%s", $today, $filename[$i])) if ($today);			# �{��
	push(@RANK_Y, sprintf("%06d:%s", $yesterday, $filename[$i])) if ($yesterday);	# ���

	flock(LOG,8);
	close(LOG);
}

@RANK_A = sort({$b cmp $a} @RANK_A);
@RANK_T = sort({$b cmp $a} @RANK_T);
@RANK_Y = sort({$b cmp $a} @RANK_Y);


&html_head;

print "<TABLE border=1 cellspacing=0 cellpadding=1>";
print "<TR><TH>�y�[�W</TH><TH>�ŏI�X�V����</TH><TH>�ŏI�L�^IP</TH><TH>����</TH><TH>�{��</TH><TH>���</TH></TR>";
$SUM_all = $SUM_today = $SUM_yesterday = 0;
foreach $line (@LOG) {
	($logname, $date,$time,$all,$today,$yesterday,$ip) = split(/#/, $line);
	$SUM_all += $all;
	$SUM_today += $today;
	$SUM_yesterday += $yesterday;
	print "<TR align=right><TH>$logname</TH><TD>$date $time</TD><TD>$ip</TD><TD>$all</TD><TD>$today</TD><TD>$yesterday</TD></TR>";
}
print "<TR align=right><TH>�T�C�g�v</TH><TD>�@</TD><TD>�@</TD><TD>$SUM_all</TD><TD>$SUM_today</TD><TD>$SUM_yesterday</TD></TR>";
print "</TABLE>\n<BR>\n";

print "<TABLE border=0 cellspacing=0 cellpadding=0><TR><TD valign=top>\n";
&Macro_PutTable('����', $SUM_all, @RANK_A);
print "</TD><TD valign=top>\n";
&Macro_PutTable('�{��', $SUM_today, @RANK_T);
print "</TD><TD valign=top>\n";
&Macro_PutTable('���', $SUM_yesterday, @RANK_Y);
print "</TD></TR></TABLE>\n";

&html_tail;
exit(0);


sub Macro_PutTable {
	local($title, $total, @array) = @_;

	print "<TABLE border=1 cellspacing=0 cellpadding=1>";
	print "<TR><TH colspan=3>$title�����L���O<BR>�T�C�g�v : $total</TH></TR>";
	$i = 1;
	$ave = 0;
	foreach $line (@array) {
		($n, $data) = ($line =~ /^(\d\d\d\d\d\d):(.*)/);
		$ave_old = $ave;
		$n = int($n);
		$ave = sprintf("%2.1f",($n*100)/$total) if ($total);
		$width = int($ave);
		if ($ave eq $ave_old) {
			print "<TR><TD>�@</TD><TD align=right>$data</TD><TD><IMG src=b.gif height=10 width=$width> $n</TD></TR>";
		} else {
			print "<TR><TD>${i}��</TD><TD align=right>$data</TD><TD><IMG src=b.gif height=10 width=$width> $n (${ave}%)</TD></TR>";
			$i++;
		}
	}
	print "</TABLE>\n";
}


### [�G���[�o��]
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
	<META http-equiv=\"Content-Type\" content=\"text/html; charset=Shift_JIS\">
	<META http-equiv=\"Content-Style-Type\" content=\"text/css\">
	<TITLE>�Ղ��J�E���^</TITLE>
	<STYLE type=\"text/css\"><!--
		BODY    {font-family:Arial,Verdana}
		A       {text-decoration:none; font-weight:bold}
		A:hover {text-decoration: underline}
	--></STYLE>
</HEAD>

<BODY bgcolor=#ffffff text=#7e2828 link=#7726c8 alink=#5c4fff vlink=#ff5959>

<B><FONT size=+1>�Ղ��J�E���^ $ver</FONT></B>
<HR>

END
}


;### HTML �����ۂ̕���
sub html_tail {
	print "\n<HR>\n<DIV align=right><A href=\"http://tech.millto.net/~fuka/\">[Petit-Counter $ver] / &copy;2000 Enogu Fukashigi\@YugenKoubou</A></DIV>\n</BODY>\n</HTML>\n";
}
