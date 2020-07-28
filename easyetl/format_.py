import csv
import sys

def row_formater(f):

    header_length = 0
    rows = 0

    reader = csv.reader(
                                  (line.replace('\0','')
                                       .replace('\t',',')
                                       .replace('【大咖每日谈】齐隽教授 | BPH,除了药物治疗还能拿它怎么办？','"【大咖每日谈】齐隽教授 | BPH,除了药物治疗还能拿它怎么办？"')
                                       .replace('【大咖每日谈】夏术阶教授 | 从“有刀”到"','【大咖每日谈】夏术阶教授 | 从“有刀”到')
                                  ) for line in f
                               )

    for row in reader:
        if header_length == 0:
            header_length = len(row)

        rows += 1
        yield(row,header_length)

    print(rows)

def format_data_(file_name):

    try:
        with open(file_name,'r') as f:
            for row in row_formater(f):
                yield(row)

    except  UnicodeDecodeError:

        print('source file encoding problem try utf-16')
        with open(file_name,'r',encoding='utf-16') as f:
            for row in row_formater(f):
                yield(row)


# poor implementation shake it!!!

def track_format_struc_(data_formated_rows):
        
    for row,header_length in data_formated_rows:

        row_length = len(row)

        if row_length == header_length + 1:

            cut_pos = row_length -3
            Last = row[-1:]
            Fix = row[-3] + ',' + row[-2]
            new_row = row[0:cut_pos ]
            new_row.append(Fix)
            new_row+=Last
            yield(new_row)

        elif row_length == header_length + 2:
            
            cut_pos = row_length - 5
            Last = row[-1:]
            Fix = row[-3] + ',' + row[-2]
            Fix2 = row[-5] + ',' + row[-4]
            new_row = row[0:cut_pos ]
            new_row.append(Fix2)
            new_row.append(Fix)
            new_row+=Last
            yield(new_row)
            

        elif row_length != header_length:

            print(row)

        else:

            yield(row)


def share_format_struc_(data_formated_rows):
        
    for row,header_length in data_formated_rows:

        row_length = len(row)

        if row_length == header_length + 1:
            
            cut_pos = row_length -5
            Last = row[-3:]
            Fix = row[-5] + ',' + row[-4]
            new_row = row[0:cut_pos ]
            new_row.append(Fix)
            new_row+=Last
            
            yield(new_row)

        elif row_length != header_length:

            print(row)

        else:
            yield(row)


def final_writer_(structure_formated_rows,output_name):

    with open(output_name,'w') as f:
        writer =csv.writer(f,delimiter=',',quotechar='"',quoting=csv.QUOTE_MINIMAL)
        for row in structure_formated_rows:
            writer.writerow(row)



def tracker_final_chain(file_name,output_name):
    
    final_writer_((row for row in tracker_format_struc_(format_data_(file_name))),output_name)


def share_final_chain(file_name,output_name):

    final_writer_((row for row in share_format_struc_(format_data_(file_name))),output_name)

if __name__ == '__main__':

    file_name = sys.argv[1]
    output_name = sys.argv[2]

    tracker_final_chain(file_name,output_name)


