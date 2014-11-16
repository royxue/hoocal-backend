//
//  CreateEventModel.h
//  hooCal
//
//  Created by zhongtoby on 14/11/16.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "NetManager.h"

@interface CreateEventModel : NSObject
+ (void)requestForCreateEventWithTitle:(NSString *)title Content:(NSString *)content StartTime:(NSDate *)startTime EndTime:(NSDate *)endTime Block:(StateBlock)block;
@end
