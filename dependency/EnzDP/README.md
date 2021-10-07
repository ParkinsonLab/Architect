To run EnzDP, please download the code and additional datasets from the project's repository.
This file contains details of specific modifications to be made to use EnzDP as part of Architect. 

Please refer to http://biogpu.ddns.comp.nus.edu.sg/~nguyennn/wwwEnzDP/ for more details.

# List of Modifications

In enzdp.py:
- Modify the run function of the EnzDP class to have the following conditions:
```Python
    def run(self, RES_directory=None):
        logging.info("Started.")
        subPID = ""
        try:
            # NN added the following line.
            if RES_directory is None:
                cwd = os.getcwd()
                RES_directory = cwd
            os.chdir(ENZPRO_WD) 
            # NN added the 4th argument.			
            command = ["perl" , self.EnzProPerlScript, self.cfg['FASTA_FILE'], str(self.cfg['THRESHOLD']), self.cfg['OUTPUT_FILE'], RES_directory] 
            popen = subprocess.Popen(command, bufsize=0, stdout=subprocess.PIPE, stdin=subprocess.PIPE, preexec_fn=os.setsid)
            subPID = popen.pid
            logging.info("Called perl with pid: [%s]" % subPID)
            logging.info("Command: %s" % command)
            lines_out = iter(popen.stdout.readline, '')
            for line in lines_out:
                if line.strip():
                    logging.info(line.rstrip())
        except:
            logging.critical("Running failed:\n"+traceback.format_exc())
            killProcess(subPID, "Killed process: ")
        finally:
            sleep(1)
            killProcess(subPID, "Finally killed process: ")
        logging.info("Stoped.")
```

In source/run/EnzPro.pl:
- In the INPUT section at the beginning of the file, define the following:
```perl
$resDir = "$ARGV[3]/RES";
mkdir($resDir);
```

In source/run/3-EnzPro.filter.pl:
- Modify the overlap function:
```perl
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
```
- Modify the filter_ECs function:
```perl
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
```

# Bibliography

Nguyen, N.N., et al., ENZDP: Improved enzyme annotation for metabolic network reconstruction based on domain composition profiles. Journal of Bioinformatics and Computational Biology, 2015. 13(5).
