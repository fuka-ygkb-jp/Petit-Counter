#!/usr/local/bin/perl
$ver = '1.0';     # �{�v���O�����̃o�[�W�����B�ύX���Ȃ��ŉ������B
;#+------------------------------------------------------------------------
;#|Petit-Count (�Ղ��J�E���^)                                    2000/06/07
;#|(C)2000 �s�v�c�G�̋�(http://tech.millto.net/~fuka/)
;#+------------------------------------------------------------------------
;# ������ �ݒ荀�� ������
;#+------------------------------------------------------------------------
;# [���O�t�@�C�����i�[�����f�B���N�g���̖��O]
;# ���O�p�f�B���N�g���� petit/ �z���ɍ���ĉ������B
$Dir_Log = 'log';

;# [�J�E���^�p�摜���i�[�����f�B���N�g���̖��O]
;# �J�E���^�摜�p�f�B���N�g���� petit/ �z���ɍ���ĉ������B
$Dir_Img = 'image';

;# [�J�E���^�̃C���[�W�̖��O(�W���Ŏg�p���镨)]
$DigitName = 'fuksan';

;# [gifcat.pl�̍ݏ�]�@���ʏ�͕ύX���Ȃ��ŉ�������
$gifcat = './gifcat.pl';


#+------------------------------------------------------------------------
# (�ݒ肱���܂�)
#+------------------------------------------------------------------------
# ����������͕�����l�����M���ĉ������B
# �@(�^�u�̃T�C�Y�E[4]�A�ܕԂ��E[����]���Y��ɕ\������܂�)
#+------------------------------------------------------------------------
#|&main
#+------------------------------------------------------------------------
&Macro_Setup;
if ($ENV{'REMOTE_ADDR'} eq $ip) {		# �d���A�N�Z�X�͋L�^���Ȃ�
	&Macro_Output;
} else {
	&Macro_Count;
	&Macro_SaveData;
	&Macro_Output;
}
exit(0);


#+------------------------------------------------------------------------
#|�v���O�����̗���Ƃ��ẴT�u���[�`��
#+------------------------------------------------------------------------
### �e�평����
sub Macro_Setup {
	$Digit = 0;
	$ENV{'TZ'} = 'JST-9';

	### ���ݎ����̎擾
	($sec,$min,$hour,$day,$month,$year,$youbi,$total) = localtime(time);
	@table_youbi = ('Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat');
	$RUN_DATE = sprintf("%4d/%02d/%02d(%s)",1900+$year,$month+1,$day,$table_youbi[$youbi]);
	$RUN_TIME = sprintf("%02d:%02d:%02d",$hour,$min,$sec);

	### �����擾
	foreach $data (split(/&/, $ENV{'QUERY_STRING'})) {
		($key , $val) = split(/=/,$data);
		$P{$key} = $val;
	}

	# ���O�t�@�C����
	$filename = $P{LOG};

	# ���샂�[�h
	if    ($P{MODE} eq 'a') { $OutMode = 'a'; }		# ���J�E���g
	elsif ($P{MODE} eq 't') { $OutMode = 't'; }		# �{���J�E���g
	elsif ($P{MODE} eq 'y') { $OutMode = 'y'; }		# ����J�E���g
	elsif ($P{MODE} eq 'w') { $OutMode = 'w'; }		# �����\��
	else                    { $OutMode = 'a'; }		# ����ȊO

	# ����
	if ($P{DIGIT} > 9) { &Macro_PutError('e0001'); }
	else               { $Digit = $P{DIGIT}-1; }

	# �t�H���g��
	$DigitName = $P{FONT} if ($P{FONT} ne '');

	### �f�B���N�g�������C��
	$Dir_Img = "./${Dir_Img}/${DigitName}/";		# �t�H���g�i�[�f�B���N�g��
	$Dir_Log = "./$Dir_Log/";						# ���O�i�[�f�B���N�g��

	### �I�v�V�����w�肪�Ȃ���΃��O�\�����[�h(�����ŏI���)
	if ($ENV{'QUERY_STRING'} eq '') {
		require './ps.pl';
	}

	### �����\�����[�h�������炱���ŏI���
	if ($OutMode eq 'w') {
		$RUN_TIME = sprintf("%02dc%02d",$hour,$min);
		$Digit = 0;
		print &Func_PutGIF($RUN_TIME);
		exit(0);
	}

	### ���O���J��
	unless (open(LOG,"+<${Dir_Log}${filename}.log")) { &Macro_PutError('e0000'); }
	flock(LOG,2);
	chop($line = <LOG>);
	$line = "${RUN_DATE}#${RUN_TIME}#0#0#0#" if ($line eq '');				#���߂Ă̋L�^�Ȃ珉����

	($date,$time,$all,$today,$yesterday,$ip) = split(/#/,$line);
}


### [�J�E���g����]
sub Macro_Count {
	$all++;
	if($RUN_DATE ne $date) {
		$yesterday = $today;
		$today = 1;
	} else { $today++; }
}


### [�t�@�C���ɕۑ�����]
sub Macro_SaveData {
	seek(LOG,0,0);
	print LOG "${RUN_DATE}#${RUN_TIME}#${all}#${today}#${yesterday}#$ENV{'REMOTE_ADDR'}\n";
	truncate(LOG,tell);
	flock(LOG,8);
	close(LOG);
}


### [�o�͂���]
sub Macro_Output {
	if ($OutMode eq 'a')    { print &Func_PutGIF($all); }
	elsif ($OutMode eq 't') { print &Func_PutGIF($today); }
	elsif ($OutMode eq 'y') { print &Func_PutGIF($yesterday); }
}


### [gif���o��]
sub Func_PutGIF {
	local($Data) = @_;
	local($i,$n,@array);

	require "$gifcat";
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);

	### �������w�肳�ꂽ��A����Ȃ�����0�ŕ₤
	$Data = ('0'x($Digit-(length($Data)-1))).$Data if (length($Data)-1 < $Digit);

	for ($i=0 ; $i < length($Data) ; $i++) {
		$n = substr($Data, $i, 1);
		push(@array, "${Dir_Img}${n}${DigitName}.gif");
	}

	return &gifcat'gifcat(@array);
}


### [�G���[�o��]
sub Macro_PutError {
	local ($code) = @_;

	require "$gifcat";
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);

	# e0000 = �t�@�C���I�[�v�����s
	# e0001 = �������ӂ�
	# e1111 = �����ȃI�v�V����
	for ($i=0 ; $i < length($code) ; $i++) {
		$n = substr($code, $i, 1);
		push(@Digit, "./${n}.gif");
	}
	print &gifcat'gifcat(@Digit);
	exit(1);
}
