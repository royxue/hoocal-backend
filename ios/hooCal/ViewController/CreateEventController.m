//
//  CreateEventController.m
//  hooCal
//
//  Created by zhongtoby on 14/11/16.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import "CreateEventController.h"
#import <DateTools.h>
#import <ActionSheetDatePicker.h>
#import "CreateEventModel.h"
@interface CreateEventController ()<UITextViewDelegate, UITableViewDelegate>

@property (strong, nonatomic) IBOutlet UITextField *titleField;
@property (strong, nonatomic) IBOutlet UITextView *content;
@property (strong, nonatomic) IBOutlet UITableViewCell *startTimeCell;
@property (strong, nonatomic) IBOutlet UITableViewCell *endTimeCell;
@property (strong, nonatomic) ActionSheetDatePicker *datePicker;
@property (strong, nonatomic) NSDate *startTime;
@property (strong, nonatomic) NSDate *endTime;
@end
@implementation CreateEventController
- (void)viewDidLoad {
    [super viewDidLoad];
    [self setDetailTextInCell:_startTimeCell WithDate:[NSDate date]];
    [self setDetailTextInCell:_endTimeCell WithDate:[[NSDate date] dateByAddingDays:1]];
}

#pragma mark - action
- (IBAction)cancel:(id)sender {
    [self.navigationController dismissViewControllerAnimated:YES completion:nil];
}

- (IBAction)add:(id)sender {
    [CreateEventModel requestForCreateEventWithTitle:_titleField.text Content:_content.text StartTime:_startTime EndTime:_endTime Block:^(NSInteger state, NSDictionary *dict) {
        
    }];
}

#pragma mark - Tools
- (void)setDetailTextInCell:(UITableViewCell *)cell WithDate:(NSDate *)date {
    cell.detailTextLabel.text = [NSString stringWithFormat:@"%ld年%ld月%ld日 %ld时%ld分", (long)date.year, (long)date.month, (long)date.day, date.hour, date.minute];
    if (cell == _startTimeCell) {
        _startTime = date;
    } else if (cell == _endTimeCell) {
        _endTime = date;
    }
}

#pragma mark - UITableViewDelegate
- (void)tableView:(UITableView *)tableView didSelectRowAtIndexPath:(NSIndexPath *)indexPath {
    if (indexPath.section == 1) {
        if (indexPath.row == 0) {
            [self changeCell:_startTimeCell FromDate:_startTime];
        } else if (indexPath.row == 1) {
            [self changeCell:_endTimeCell FromDate:_endTime];
        }
        [_datePicker showActionSheetPicker];
    }
}

#pragma mark - lazy Method
- (ActionSheetDatePicker *)changeCell:(UITableViewCell *)cell FromDate:(NSDate *)date {
    if (!_datePicker) {
        __weak CreateEventController *weakSelf = self;
        _datePicker = [[ActionSheetDatePicker alloc] initWithTitle:@"" datePickerMode:UIDatePickerModeDateAndTime selectedDate:date doneBlock:^(ActionSheetDatePicker *picker, id selectedDate, id origin) {
            [weakSelf setDetailTextInCell:cell WithDate:selectedDate];
        } cancelBlock:^(ActionSheetDatePicker *picker) {
            
        } origin:cell];
    }
    return _datePicker;
}

#pragma mark - UITextViewDelegate
- (void)textViewDidBeginEditing:(UITextView *)textView {
    textView.textColor = [UIColor blackColor];
    if ([textView.text isEqualToString:@"内容"]) {
        textView.text = @"";
    }
}
- (void)textViewDidEndEditing:(UITextView *)textView {
    if (textView.text.length == 0) {
        textView.text = @"内容";
        textView.textColor = [UIColor lightTextColor];
    }
}
@end
