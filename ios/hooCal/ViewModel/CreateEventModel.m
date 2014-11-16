//
//  CreateEventModel.m
//  hooCal
//
//  Created by zhongtoby on 14/11/16.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import "CreateEventModel.h"
#import "NetManager.h"
#import <NSDate+DateTools.h>

@implementation CreateEventModel
+ (void)requestForCreateEventWithTitle:(NSString *)title Content:(NSString *)content StartTime:(NSDate *)startTime EndTime:(NSDate *)endTime Block:(StateBlock)block {
    if (!(title && title.length > 0)) {
        block(failed, nil);
        return;
    }
    if (!content) {
        content = @"";
    }
    if (!startTime || !endTime) {
        block(failed, nil);
        return;
    }
    if ([endTime isEarlierThan:startTime]) {
        block(failed, nil);
        return;
    }
    NSDictionary *dict = @{@"title" : title, @"content" : content, @"start_time" : @([startTime timeIntervalSince1970]), @"end_time" : @([endTime timeIntervalSince1970])};
    [[NetManager shareInstance] requestForCreateEventWithDict:dict Block:^(NSInteger state, NSDictionary *dict) {
        
    }];
    
}
@end
