mkdir -p Scripts

TEMPLATE=TEMPLATE_eficaz.sh
i=0
j=1

for file in `ls Split_seqs`; do

	echo $file

	if [ $j -eq 1 ]; then 
		file1=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 2 ]; then 
		file2=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 3 ]; then 
		file3=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 4 ]; then 
		file4=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 5 ]; then 
		file5=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 6 ]; then 
		file6=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 7 ]; then 
		file7=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 8 ]; then 
		file8=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 9 ]; then 
		file9=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 10 ]; then 
		file10=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 11 ]; then 
		file11=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 12 ]; then 
		file12=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 13 ]; then 
		file13=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 14 ]; then 
		file14=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 15 ]; then 
		file15=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 16 ]; then 
		file16=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 17 ]; then 
		file17=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 18 ]; then 
		file18=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 19 ]; then 
		file19=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 20 ]; then 
		file20=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 21 ]; then 
		file21=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 22 ]; then 
		file22=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 23 ]; then 
		file23=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 24 ]; then 
		file24=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 25 ]; then 
		file25=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 26 ]; then 
		file26=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 27 ]; then 
		file27=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 28 ]; then 
		file28=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 29 ]; then 
		file29=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 30 ]; then 
		file30=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 31 ]; then 
		file31=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 32 ]; then 
		file32=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 33 ]; then 
		file33=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 34 ]; then 
		file34=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 35 ]; then 
		file35=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 36 ]; then 
		file36=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 37 ]; then 
		file37=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 38 ]; then 
		file38=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 39 ]; then 
		file39=$file;
		j=$(($j + 1))
		
	elif [ $j -eq 40 ]; then 
		file40=$file;
		cat $TEMPLATE | sed "s|SEQUENCE_FILENAME_X1|${file1}|g" | sed "s|SEQUENCE_FILENAME_X2|${file2}|g" | sed "s|SEQUENCE_FILENAME_X3|${file3}|g" | sed "s|SEQUENCE_FILENAME_X4|${file4}|g" | sed "s|SEQUENCE_FILENAME_X5|${file5}|g" | sed "s|SEQUENCE_FILENAME_X6|${file6}|g" | sed "s|SEQUENCE_FILENAME_X7|${file7}|g" | sed "s|SEQUENCE_FILENAME_X8|${file8}|g" | sed "s|SEQUENCE_FILENAME_X9|${file9}|g" | sed "s|SEQUENCE_FILENAME_10|${file10}|g" | sed "s|SEQUENCE_FILENAME_11|${file11}|g" | sed "s|SEQUENCE_FILENAME_12|${file12}|g" | sed "s|SEQUENCE_FILENAME_13|${file13}|g" | sed "s|SEQUENCE_FILENAME_14|${file14}|g" | sed "s|SEQUENCE_FILENAME_15|${file15}|g" | sed "s|SEQUENCE_FILENAME_16|${file16}|g" | sed "s|SEQUENCE_FILENAME_17|${file17}|g" | sed "s|SEQUENCE_FILENAME_18|${file18}|g" | sed "s|SEQUENCE_FILENAME_19|${file19}|g" | sed "s|SEQUENCE_FILENAME_20|${file20}|g" | sed "s|SEQUENCE_FILENAME_21|${file21}|g" | sed "s|SEQUENCE_FILENAME_22|${file22}|g" | sed "s|SEQUENCE_FILENAME_23|${file23}|g" | sed "s|SEQUENCE_FILENAME_24|${file24}|g" | sed "s|SEQUENCE_FILENAME_25|${file25}|g" | sed "s|SEQUENCE_FILENAME_26|${file26}|g" | sed "s|SEQUENCE_FILENAME_27|${file27}|g" | sed "s|SEQUENCE_FILENAME_28|${file28}|g" | sed "s|SEQUENCE_FILENAME_29|${file29}|g" | sed "s|SEQUENCE_FILENAME_30|${file30}|g" | sed "s|SEQUENCE_FILENAME_31|${file31}|g" | sed "s|SEQUENCE_FILENAME_32|${file32}|g" | sed "s|SEQUENCE_FILENAME_33|${file33}|g" | sed "s|SEQUENCE_FILENAME_34|${file34}|g" | sed "s|SEQUENCE_FILENAME_35|${file35}|g" | sed "s|SEQUENCE_FILENAME_36|${file36}|g" | sed "s|SEQUENCE_FILENAME_37|${file37}|g" | sed "s|SEQUENCE_FILENAME_38|${file38}|g" | sed "s|SEQUENCE_FILENAME_39|${file39}|g" | sed "s|SEQUENCE_FILENAME_40|${file40}|g" > Scripts/eficaz_${i}.sh;
		echo $i, $j, $file
		j=1;
	fi
	
	i=$(($i + 1))
	
done