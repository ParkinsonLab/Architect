#! perl -w
use List::Util qw(max min);

### INPUT ###
$ECListFile = "../../data/EC.list";
$addedResFile = $ARGV[0];

$CUT_OFF = $ARGV[1]; # print result with expected precision not lower than this cut-off

### OUTPUT ###
$outFile = $ARGV[2];

$domId = 16;
$relGAId = 6;
$preId	= 2;
#=================================================
# Read EC list file:
%ECsOfECID = ();
open(FILE, $ECListFile) ||die;
while(<FILE>){
	chomp($_);
	($ECID,$ECs) = split(/\t/,$_);
	$ECsOfECID {$ECID} = $ECs;
} 
close(FILE);
#=================================================
# Read the input file:
open(FILE, $addedResFile) ||die "no input\n";
%ECIDOfSgr = ();
%ResOfORF = ();
while(<FILE>){
	($sgr, $ORF) = split(/\t/,$_);
	($ECID) = split(/\.sgr/,$sgr); 

	$ECIDOfSgr{$sgr} = $ECID;

	if (exists 	$ResOfORF {$ORF}){
		$ResOfORF {$ORF} = 	$ResOfORF {$ORF} . $_;
	}else{ $ResOfORF {$ORF} = $_;}
}
close(FILE);

#=================================================
# Filtering for each ORF:
#$total = scalar keys %ResOfORF;
#print $total ." lines\n";
$outFileRaw = $outFile.".raw";
open(OUT,">",$outFileRaw);
$i = 0;
#$startTime = time;
@ALLRES = ();
foreach $orf(keys %ResOfORF){
	#print "[$i/$total]:  $orf  [elapsed " .(time - $startTime). " seconds]         \r";
	$i++;
	$gBinSize = 1;
	@ScoreRes = filterECs($ResOfORF{$orf},$orf);

	print OUT ">$orf\n";
	foreach (@ScoreRes){
		my @tmp = split(/\s/,$_);
		next if ($tmp[3] < $CUT_OFF); 
		print OUT $_ ;#."\n";	
		push(@ALLRES,$_);
	}
}
close(OUT);
#print "\n DONE! \n";
#print "Raw result was written to file [$outFileRaw]\n";

%BSAndProbOf 	= ();
#%HitSiteOf 		= ();
foreach(@ALLRES){#ECm_46.sgr1	myProtein	1.000	1.000	1.616	1.000	1.465	1.000	1.691	1.000	1.323	1.000	0	1147.8	1	0	1147.2	0	1147.2	1	714	1577	2292	AS:122/255|BD:11/0|	
	@Cols = split;
	$sgr = $Cols[0];
	$pid = $Cols[1];
	($ecid) = split(/\Q.sgr\E/,$sgr);
	$ECs = $ECsOfECID{$ecid};
	@ECArr = split(/\|/,$ECs);
	foreach $ec(@ECArr){
		if (exists $BSAndProbOf{$pid."\t".$ec}){
				$BSAndProbOf{$pid."\t".$ec} = $BSAndProbOf{$pid."\t".$ec} .$Cols[3] .":".$Cols[16]."|";
		}else { $BSAndProbOf{$pid."\t".$ec} = $Cols[3] .":".$Cols[16]."|";}	# myprobability and best domain score

	};
};


foreach (keys %BSAndProbOf){
	$BestScoreOf  {$_} = findBestScoreOf($BSAndProbOf{$_});
};

#Print Result:
open(OUT,">",$outFile);
foreach(keys %BestScoreOf){
	print OUT $_ ."\t". $BestScoreOf{$_}. "\n";
};
close(OUT);
#print "Result was written to file [$outFile]\n";
##################################################

sub findBestScoreOf{
	my $str = shift;
	my @Arr = split(/\|/,$str);
	@Arr = 	sort {
				($proA,$bscA) = split(/:/,$a);
				($proB,$bscB) = split(/:/,$b);
				if ($proA == $proB){ return ($bscB <=> $bscA)}
				else{return ($proB <=> $proB)};
			} @Arr;

	my $res = $Arr[0];
	my ($pro,$bsc) = split(/\:/,$res);
	$res = "$pro\t$bsc";
	return $res;
};

sub findBestHitSite{
	my $a = shift;
	
	return $a;
};


#ECm_36.sgr1	myProtein	0.181	0.181	0.800	1.000	0.714	1.000	0.817	1.000	0.614	1.000	7.2e-171	554.5	2	4.9e-161	522.1	4.9e-161	522.1	8	379	383	752	5.9e-13	34.8	32	371	782	1096
# sorted by best domain bscore already.

sub filterECs{
	my $lines = shift;
	my $orf = shift; #Nirvana Nursimulu
	my @LINES = split(/\n/,$lines);
	$nLine = $#LINES;

	my $maxBS = 0;
	my $minBS = 1e15;

	my @AoA = ();
	my @Good = ();

	foreach my $line (@LINES){
		my @TMP = split(/\s/,$line);	# $TMP[16] = best domain BS
		#$maxBS = $TMP[$domId] if ($maxBS < $TMP[$domId]);
		$maxBS = max($maxBS,$TMP[$domId]);
		#$minBS = $TMP[$domId] if ($minBS > $TMP[$domId]);
		$minBS = min($minBS,$TMP[$domId]);
		push @AoA, [@TMP];
		push @Good, 1;
	};

	my $binSize = ($maxBS-$minBS)/10;
	$gBinSize = $binSize;
	return if ($binSize == 0.0);

#Sorting: by bin first, then by RelGA
	@AoA = sort{
		if ( int($a->[$domId]/$binSize) == int($b->[$domId]/$binSize)) {	# same bin:
			return ($b->[$relGAId]  <=> $a->[$relGAId]); # $TMP[$relGAId] = relGA
		}
		else{	#different bins:
			return ($b->[$domId] <=> $a->[$domId]);
		}
	} @AoA;

	
#find best domain alignment start and end:
	for $i (0 .. $nLine){
		$iSt = 1; $iEd = 2;
		for $k ( ($domId+1) .. (scalar $AoA[$i])){
		next if (!exists $AoA[$i][$k]);
		next if (!exists $AoA[$i][$domId]);
		if ($AoA[$i][$k] == $AoA[$i][$domId]){
			$iSt = $AoA[$i][$k+3];
			$iEd = $AoA[$i][$k+4];
			last;
		}};
		$St[$i] = $iSt;
		$Ed[$i] = $iEd;
	};# for i=0..nLine

# Check each line:
	for $i (1 .. $#AoA){
		$subSetFlag = 0;
		for $j (0 .. ($i-1)){
			next if ($Good[$j] <1);
			my $iSgr = $AoA[$i][0];
			my $jSgr = $AoA[$j][0];
			if ((isSubSet($iSgr, $jSgr)==1) or (isSubSet($jSgr, $iSgr)==1)){;	# subset 
				$subSetFlag = 1;
				last;
			};
		};# for j first
		next if ($subSetFlag == 1);

		for $j (0 .. ($i-1)){
			next if ($Good[$j] <1);		# Added 12-Apr
			my $iSgr = $AoA[$i][0]; #NNursimulu
			my $thisEC = $ECsOfECID{$ECIDOfSgr{$iSgr}}; #NNursimulu
			if (overlap($St[$j], $Ed[$j], $St[$i], $Ed[$i], $orf, $thisEC) == 1){ #NNursimulu
				next if ($AoA[$i][$preId] > 2*$AoA[$j][$preId]);	# precision of j is too bad compared too current i one.
				$Good[$i] = 0;
				#print "Line ".($i+2)." is bad because of ".($j+2)."\n\n\n";
				last;
			};
		}; # for j second.

	};

	my @Res = ();
	for my $i (0 .. $#AoA){		
		my $str = "";
		my @tmpArr = @{$AoA[$i]};
		$str = $str .$_ ."\t" foreach(@tmpArr);
		
		next if ($Good[$i] <1);
		$str = "BAD ". $str if ($Good[$i] < 1);

		push(@Res,$str."\n");
	};

	return @Res;
};# sub


sub isSubSet{
	my $a = shift;
	my $b = shift;
	
	$aEC = $ECsOfECID{$ECIDOfSgr{$a}};
	$bEC = $ECsOfECID{$ECIDOfSgr{$b}};

	@ECArr = split(/\|/,$aEC);
	foreach my $ec (@ECArr){
		my $replacements = $ec =~ s/\.-//g;
		my $tmpEC = "|$ec";
		$tmpEC = "|$ec." if ($replacements >0);
		$tmpEC = "|$ec|" if ($replacements <1);
		return 0 if (index("|$bEC|",$tmpEC)<0)
	};
	#print "		SUB-SET!\n";
	return 1;
};

sub overlap{
	my $a = shift;
	my $b = shift;
	my $c = shift;
	my $d = shift;
	my $orf = shift; # NNursimulu
	my $thisEC = shift; #NNursimulu
	
	my $st = max($a,$c); 	
	my $ed = min($b,$d);

	my $distAB = $b - $a;
	my $distCD = $d - $c;
	my $distOV = $ed - $st;
	my $minDist = min($distAB, $distCD);
	
	print "[NNursimulu]: Overlap fix for $thisEC predicted for $orf. One of the sites is one amino acid long (domain intervals [$a $b] and [$c $d])." if ($minDist == 0 && $distOV == 0); # Nirvana Nursimulu
	return 1 if ($minDist == 0 && $distOV == 0); # Added by Nirvana Nursimulu on January 20th 2020.
	
	my $overlapRatio = 0.0+ $distOV / $minDist;

	#print "[$a $b] and [$c $d]:";
	#print " have overlap [$st $ed] = $overlapRatio" if ($overlapRatio > 0.5);
	#print "\n\n";
	return 1 if ($overlapRatio > 0.5);
	return 0;
};
