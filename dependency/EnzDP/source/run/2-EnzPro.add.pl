#! perl -w
# adding expected precision for each prediction.

$zero = 1e-10;

$rawResFile = $ARGV[0];

$hmmDir		= "../../HMMs/";
$outFile	= $ARGV[1];

$logisticProg = "java -cp .:stanford-ner.jar Logistic";

#=================================================
# Read the raw result file:
%ResLinesOfSgr = ();

open(FILE,$rawResFile);
#3.2.1.1.sgr8	AO090023000944	3.7e-242	804.1	1	4.3e-242	803.8	5.4e-245	803.8	16	502	10	498
#3.2.1.1.sgr8	AO090120000196	3.7e-242	804.1	1	4.3e-242	803.8	5.4e-245	803.8	16	502	10	498
while(<FILE>){
	next if (/^>/);
	next if (/^\s+$/);
	($sgr) = split(/\s+/,$_);
	if (exists $ResLinesOfSgr {$sgr}){
		$ResLinesOfSgr {$sgr} = $ResLinesOfSgr {$sgr} . $_;
	}
	else{
		$ResLinesOfSgr {$sgr} = $_;
	}
}
close(FILE);

#=================================================
# Read the threshold file:
%GAOfSgr 	= ();
%OptOfSgr 	= ();
%noFNOfSgr 	= ();
%noFPOfSgr 	= ();
%PreOpt		= ();
%PreGA 		= ();
%PrenoFN	= ();
%PrenoFP	= ();

foreach $sgr (keys %ResLinesOfSgr){
	next if (! -e $hmmDir ."$sgr.hmm");
	$thresholdFile = $hmmDir ."$sgr.hmm.threshold";
	$HitScoreForSgr {$sgr} = "";
	open(FILE, $thresholdFile);
	while(<FILE>){
		if (/noFN/){
			(undef,$noFN, $noFNpre) = split(/\t/,$_);
			$noFNOfSgr {$sgr} = $noFN;
			$PrenoFN   {$sgr} = sprintf("%.3f",$noFNpre/100);
		};	
		if (/noFP/){
			(undef,$noFP, $noFPpre) = split(/\t/,$_);
			$noFPOfSgr {$sgr} = $noFP;
			$PrenoFP   {$sgr} = sprintf("%.3f",$noFPpre/100);
		};	
		if (/GA/){
			(undef,$ga, $gaPre) = split(/\t/,$_);
			$GAOfSgr {$sgr} = $ga;
			$PreGA	 {$sgr} = sprintf("%.3f",$gaPre/100);
		};
		if (/Opt/){
			(undef,$opt, $pre) = split(/\t/,$_);
			$OptOfSgr {$sgr} = $opt;
			$PreOpt   {$sgr} = sprintf("%.3f",$pre/100);
		};	
			
		next if (/^>/);

		$HitScoreForSgr {$sgr} = $HitScoreForSgr {$sgr} . $_;
	};
	close(FILE);	
} # foreach sub group

#=================================================
# Add expected precision score:
open(OUTPUT,">$outFile.tmp");
@HitBScores = ();
@HitPrecisions = ();

foreach $sgr (keys %ResLinesOfSgr){
	# extract the hit scores for this sgr profile (from benchmark SP):
	@HitScoreArrTmp 	= split(/\n/,$HitScoreForSgr {$sgr});
	@HitBScores 		= ();
	@HitPrecisions 		= ();
	%KnownLabelOf 		= ();

	$nHits = 0;
	$nN = 0;
	$lSE = 1e3;
	$hN	= 0.0;

	foreach $line (@HitScoreArrTmp){
		#print $line."\n" if ($sgr =~ /\Q1.1.1.103.sgr1\E/);
		($bscore,$label,$pre) = split(/\t/,$line);
		push(@HitBScores,$bscore);
		push(@HitPrecisions,$pre);
		$KnownLabelOf{$bscore} = $label;

		$nHits++;
		if ($label =~ /N/){
			$hN = $bscore if ( (0.0+$bscore) > ($hN+0.0));
			$nN++;
			#print $bscore ."\t".$hN."\n" if ($sgr =~ /\Q1.1.1.103.sgr1\E/);
		}else{
			$lSE = $bscore if ((0.0+$bscore) < $lSE);
		};
	}
	next if ($nHits < 1);
	# process the result:
	@ResLineArr 	= split(/\n/, $ResLinesOfSgr {$sgr});
	foreach $line(@ResLineArr){
		($mySgr, $myORF, $myEVal, $myBScore, @remains) = split(/\s+/,$line);
		

		$myRelOpt 	= $myBScore / ( $OptOfSgr	{$mySgr} + $zero);# relative of myBScore to the optimal score;
		$myRelGA  	= $myBScore / ( $GAOfSgr 	{$mySgr} + $zero);# relative of myBScore to the gathering score; 
		#print $line."\n" if ($noFNOfSgr 	{$mySgr} eq "");
		#print $zero."\n" if ($zero eq "");
		$myRelnoFN 	= $myBScore / ( $noFNOfSgr 	{$mySgr} + $zero);# relative of myBScore to the noFN score; 

		$myRelnoFP 	= $myBScore / ( $noFPOfSgr 	{$mySgr} + $zero);# relative of myBScore to the noFP score; 

		$myRelOpt 	= sprintf("%.3f",$myRelOpt);
		$myRelGA 	= sprintf("%.3f",$myRelGA);
		$myRelnoFN 	= sprintf("%.3f",$myRelnoFN);
		$myRelnoFP 	= sprintf("%.3f",$myRelnoFP);

		$myPrecision = calcPrecision($myBScore);

		$myProbability = $myPrecision;
		
		if ($myRelGA <1.0){
			$coef = 1.2 + log(1/$myRelGA);
			$myProbability = $myProbability / $coef;
		};
		#$myProbability = calcProb($myBScore);

		#chomp($myProbability);

		$myProbability 	= sprintf("%.3f",$myProbability);

		print OUTPUT $mySgr ."\t". $myORF ."\t". $myPrecision ."\t". $myProbability. "\t". $myRelOpt. "\t". $PreOpt{$sgr}. "\t". $myRelGA ."\t". $PreGA{$sgr}. "\t". $myRelnoFP. "\t". $PrenoFP{$sgr} ."\t". $myRelnoFN. "\t". $PrenoFN{$sgr} ;
		print OUTPUT "\t". $myEVal ."\t". $myBScore; 
		print OUTPUT "\t". $_ for (@remains);
		print OUTPUT "\n";
	}	
}
close(OUTPUT);

system("sort -k2,2 -k17,17nr -k12,12nr -k11,11nr -k10,10nr -k9,9nr $outFile.tmp > $outFile");
unlink("$outFile.tmp");
#print "OutFile is $outFile\n";

##################################################
##################################################
##################################################

sub countHit{
	my $a = shift;
	my @Arr = split(/\|/,$a);
	my $ECCnt = 0;
	my $AllCnt = 0;
	foreach (@Arr){
		my ($ecCnt, $allCnt) = split;
		$ECCnt += $ecCnt;
		$AllCnt += $allCnt;	
	};

	return "$ECCnt/$AllCnt";
};

sub sortStandard{	
	my $a = shift;
	#print $a ."HAHAHA\n";
	my @Arr = split(/\|/,$a);
	@Arr = sort @Arr;
	my $Res = "";
	$Res = $Res.$_."|"	foreach(@Arr);
	return $Res;
};


sub calcProb{
	my $bs = shift;
	my $trainFile = "train.dat";
	my $testFile = "test.dat";
	$here = `pwd`;
	chdir("../../progs/");
	open(TMPFILE, ">$trainFile");
	foreach $score(@HitBScores){
		my $label = "1";
		$label = "2" if ($KnownLabelOf{$score} !~ /N/);
		print TMPFILE $label ." 0:1 1:". log($score)."\n";
	};
	close(TMPFILE);
	open(TMPFILE,">$testFile");
	print TMPFILE "20 0:1 1:".log($bs);
	close(TMPFILE);

	system("$logisticProg $trainFile $testFile > result.txt 2>null");

	$result =`cat result.txt`;
	
	chdir($here);
	return $result;
};#sub

#=============================
sub calcPrecision{
	my $bscore = shift;
	my $res = 0;
	my $next = $HitBScores[$#HitBScores] * 0.00;
	my $prev = $HitBScores[0] * 1.10;
	
	my $nextPrec = $HitPrecisions[$#HitPrecisions] * 0.00;
	my $prevPrec = $HitPrecisions[0] * 1.10;
	my $adjust = -1;	
	my $i = 0;
	foreach(@HitBScores){
		if ($KnownLabelOf{$_} eq "g"){
			$i++;
			next;		
		}
		if ($bscore == $_){
			$adjust = 0 if ($KnownLabelOf{$bscore} =~ /N/);
			$adjust = 1 if ($KnownLabelOf{$bscore} !~ /N/);
		};
		if ($bscore >= $_){ $next = $_; $nextPrec = $HitPrecisions[$i]; last;}
		else{ $prev = $_; $prevPrec = $HitPrecisions[$i]};
		$i++;
	}

	if ($next == $prev){ $res = $nextPrec;}
	else{
		$res = $nextPrec + ($prevPrec - $nextPrec)* ($bscore - $next)/($prev - $next);
	}
	$res = $nextPrec if ($res < 0);
	$res = $res/100;

	$res = 1.0 if ($res >1.0);


	#$res = ($res + 1*$adjust)/2 if ($adjust ==1);
	#$res = ($res + 0.25*$adjust)/1.25 if ($adjust ==0);
	
	if ($adjust == -1){	# not met
		if ($sgr =~ /\Q1.1.1.103.sgr1\E/){
			#print $lSE ."\t". $hN."\n";		
		};
		if ( ($nN>=10) and ($lSE > $hN) and ($myRelGA < 1.0) ){
			#$coef = 1.2 + log($lSE/$hN);
	#		$res = $res / $coef;
			#print $sgr."\t".$coef."\n";
		}
	};

	return sprintf("%.3f",$res);
}

