#!/usr/local/bin/perl
$ver = '2.3';     # �{�v���O�����̃o�[�W�����B�ύX���Ȃ��ŉ������B
#+------------------------------------------------------------------------
#|Petit-Count (�Ղ��J�E���^)                                    2016/08/12
#|(C)2000, 2016 �s�v�c�G�̋�(http://ygkb.jp/)
#+------------------------------------------------------------------------
# ������ �ݒ荀�� ������
#+------------------------------------------------------------------------
# [���O�t�@�C�����i�[�����f�B���N�g���̖��O]
# ���O�p�f�B���N�g���� petit/ �z���ɍ���ĉ������B
$Dir_Log = 'log';

# [�J�E���^�p�摜���i�[�����f�B���N�g���̖��O]
# �J�E���^�摜�p�f�B���N�g���� petit/ �z���ɍ���ĉ������B
$Dir_Img = 'image';

# [�J�E���^�̃C���[�W�̖��O (�W���Ŏg�p���镨)]
$DigitName = 'fuksan';

# [�J�E���g�A�b�v�����Ȃ�IP�A�h���X]
# �K��IP�A�h���X�̌`���Ŏw�肵�ĉ������B
# ���C���h�J�[�h�Ȃǂ͎g���܂���B�@�����܂ŁA���܂��I�ȕ��ƍl���ĉ������B
$DenyIP = '192.168.0.30';

# [�W�v��ʂōŏI�A�N�Z�X�҂�IP�A�h���X��\�������邩]
# ������ꍇ�� 1 ���B�@�����Ȃ��ꍇ�� 0 ���w��B
$DoPutLastIP = 1;

# [gifcat.pl�̂��肩 (�ʏ�͕ύX���Ȃ��ŉ�����)]
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
#|�v���O�����̗���Ƃ��ẴT�u���[�`��
#+------------------------------------------------------------------------
### �e�평����
sub Macro_Setup {
	$ENV{'TZ'} = 'JST-9';
	$P{DIGIT} = 0;
	$OutputOnly = 0;	# 1=�o�͂̂�

	### ���ݎ����̎擾
	$RUN_TIME = time;
	@RUN_TIME = localtime($RUN_TIME);
	$RUN_week = &Func_TotalWeek($RUN_TIME[7]);

	### �����擾
	foreach $data (split(/&/, $ENV{'QUERY_STRING'})) {
		($key , $val) = split(/=/,$data);
		$val =~ s/%([0-9A-Fa-f][0-9A-Fa-f])/pack("C",hex($1))/ge;
		$val =~ tr/+/ /;
		$val =~ s/\t//g;
		$P{$key} = $val;
	}

	# ���샂�[�h
	if ($P{MODE} =~ /^-([atyw])$/) {				# ���� - ������Ώo�͂̂�
		$P{MODE} = $1;
		$OutputOnly = 1;
	} elsif ($P{MODE} !~ /^[atyw]$/) {				# ������Ε��ʂɃ`�F�b�N
		$P{MODE} = 'a';								# �������Ȃ���΋����I�� a ��
	}

	# ����
	if ($P{DIGIT} > 20) { &Macro_PutError('e0001'); }
	else { $P{DIGIT} -= 1; }

	# �t�H���g��
	$DigitName = $P{FONT} if ($P{FONT} ne '');

	# �f�B���N�g�������C��
	$Dir_Img = "./${Dir_Img}/${DigitName}/";		# �t�H���g�i�[�f�B���N�g��
	$Dir_Log = "./${Dir_Log}/";						# ���O�i�[�f�B���N�g��

	### �I�v�V�����w�肪�Ȃ���΃��O�\�����[�h(�����ŏI���)
	if ($ENV{'QUERY_STRING'} eq '') {
		require './ps.pl';
	}

	### �����\�����[�h�������炱���ŏI���
	if ($P{MODE} eq 'w') {
		print &Func_PutGIF(sprintf("%02dc%02d",$RUN_TIME[2],$RUN_TIME[1]));
		exit(0);
	}

	### ���O���J��
	unless (open(LOG,"+<${Dir_Log}$P{LOG}.log")) { &Macro_PutError('e0000'); }
	flock(LOG,2);
	chop(@log = <LOG>);

	# ���߂Ă̋L�^�Ȃ珉����
	if ($log[0] eq '') {
		$log[0] = "PC2#${RUN_TIME}";									# �w�b�_
		$log[1] = "${RUN_TIME}#0#-";									# �e����
		$log[2] = "0#0#0#0#0#0#0#0";									# ���ʏW�v
		$log[3] = "0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0";	# ���ԕʏW�v
		$log[4] = "0#0#0#0#0#0#0";										# �j���ʏW�v
		$log[5] = "0#0#0#0#0#0";										# �T�ʏW�v
		$log[6] = "0#0#0#0#0#0#0#0#0#0#0#0";							# ���ʏW�v
		$log[7] = "0#0#0#0#0#0";										# �N�x�ʏW�v
	}

	# �ʏ폈��
	($LOG_VER, $LOG_SINCE) = split(/#/,$log[0]);
	if ($LOG_VER ne 'PC2') { &Macro_PutError('e1110'); }				# ���OVer.�s�����������~

	($LOG_TIME, $ALL, $LOG_IP) = split(/#/,$log[1]);
	@DAILY = split(/#/,$log[2]);
	@HOUR  = split(/#/,$log[3]);
	@YOUBI = split(/#/,$log[4]);
	@WEEK  = split(/#/,$log[5]);
	@MONTH = split(/#/,$log[6]);
	@YEAR  = split(/#/,$log[7]);

	# ���O�̓��t�����߂�
	@LOG_TIME = localtime($LOG_TIME);
	$LOG_week = &Func_TotalWeek($LOG_TIME[7]);
}


### [�J�E���g����]
sub Macro_Count {
	### �����Ԍo�߂��������߂�
	$n = $RUN_TIME[7] - $LOG_TIME[7];
	$n += 366 if ($n < 0);			# �N���������ꍇ�␳(n+366���o��)

	if ($n == 0) { $DAILY[0]++; }	# ������
	elsif ($n > 0) {				# n���o��
		for (1 .. $n) { unshift(@DAILY, 0); }
		$DAILY[0] = 1;
	}


	### ���T�Ԍo�߂��������߂�
	$n = $RUN_week - $LOG_week;
	$n += 53 if ($n < 0);			# �N���������ꍇ�␳(n+53�T�Ԍo��)

	if ($n == 0) { $WEEK[0]++; }	# �����T
	elsif ($n > 0) {				# n�T�Ԍo��
		for (1 .. $n) { unshift(@WEEK, 0); }
		$WEEK[0] = 1;
	}


	### ���N�Ԍo�߂��������߂�
	$n = $RUN_TIME[5] - $LOG_TIME[5];

	if (($n == 0) || ($n < 0)) { $YEAR[0]++; }	# �����N(�T�[�o�����v���Â��ꍇ�����̏���)
	elsif ($n > 0) {							# n�N�o��
		@MONTH = (0) x 12;						# ���ʏW�v��reset
		for (1 .. $n) { unshift(@YEAR, 0); }
		$YEAR[0] = 1;
	}

	$ALL++;
	$HOUR[${RUN_TIME[2]}]++;
	$YOUBI[${RUN_TIME[6]}]++;
	$MONTH[${RUN_TIME[4]}]++;
}


### [�t�@�C���ɕۑ�����]
sub Macro_SaveData {
	$log[0] = "PC2#${LOG_SINCE}";
	$log[1] = "${RUN_TIME}#${ALL}#$ENV{'REMOTE_ADDR'}";
	$log[2] = &Func_Array2Str(8,  *DAILY);					# ���ʏW�v
	$log[3] = &Func_Array2Str(24, *HOUR);					# ���ԕʏW�v
	$log[4] = &Func_Array2Str(7,  *YOUBI);					# �j���ʏW�v
	$log[5] = &Func_Array2Str(6,  *WEEK);					# �T�ʏW�v
	$log[6] = &Func_Array2Str(12, *MONTH);					# ���ʏW�v
	$log[7] = &Func_Array2Str(6,  *YEAR);					# �N�x�ʏW�v

	seek(LOG,0,0);
	foreach $line (@log) { print LOG "$line\n"; }
	truncate(LOG,tell);

	flock(LOG,8);
	close(LOG);

	### �z��̓��e����s�̕�����ɒ����֐�
	### $limit���傫�ȃf�[�^�͐؂�̂Ă�
	sub Func_Array2Str {
		local($limit, *array) = @_;
		splice(@array, $limit);
		return join("#", @array);
	}
}


### [�o�͂���]
sub Macro_Output {
	if ($P{MODE} eq 'a')    { print &Func_PutGIF($ALL); }
	elsif ($P{MODE} eq 't') { print &Func_PutGIF($DAILY[0]); }
	elsif ($P{MODE} eq 'y') { print &Func_PutGIF($DAILY[1]); }
}


### [�G���[�o��]
sub Macro_PutError {
	local ($code) = @_;

	require "$gifcat";
	print "Content-type: image/gif\n\n";
	binmode(STDOUT);

	# e0000 = �t�@�C���I�[�v�����s
	# e0001 = �������ӂ�
	# e1110 = ���O�̃o�[�W�������s��
	for ($i=0 ; $i < length($code) ; $i++) {
		$n = substr($code, $i, 1);
		push(@Digit, "./${n}.gif");
	}
	print &gifcat'gifcat(@Digit);
	exit(1);
}


### [gif���o��]
sub Func_PutGIF {
	local($Data) = @_;
	local($i,$n,@array);

	require "$gifcat";
	print "Content-type: image/gif\n";
	print "Expires: 01/01/1970 00:00:00 JST\n\n";	# �L���b�V���𖳌��ɂ���
	binmode(STDOUT);

	### �������w�肳�ꂽ��A����Ȃ�����0�ŕ₤
	$Data = ('0'x($P{DIGIT}-(length($Data)-1))).$Data if (length($Data)-1 < $P{DIGIT});

	for ($i=0 ; $i < length($Data) ; $i++) {
		$n = substr($Data, $i, 1);
		push(@array, "${Dir_Img}${n}${DigitName}.gif");
	}

	return &gifcat'gifcat(@array);
}


### �ʎZ�T�����߂�֐�
sub Func_TotalWeek {
	local($total) = @_;
	local($week);

	if ($total < 7) { $week = 0; }	# 0���Z�΍�
	else { $week = int($total/7); }

	return $week;
}
