//
//  NetManager.h
//  hooCal
//
//  Created by zhongtoby on 14/11/15.
//  Copyright (c) 2014年 hang. All rights reserved.
//

#import <Foundation/Foundation.h>
typedef NS_ENUM(NSUInteger, returnState) {
    successful = 1,
    failed
};

typedef void(^StateBlock)(NSInteger state, NSDictionary *dict);

@interface NetManager : NSObject
+ (instancetype)shareInstance;
- (void)requestForRegisterWithNickName:(NSString *)nickName Email:(NSString *)email Psw:(NSString *)psw Block:(StateBlock)block;
- (void)requestForSignInWithEmail:(NSString *)email Psw:(NSString *)psw Block:(StateBlock)block;
- (void)requestForCreateEventWithDict:(NSDictionary *)dict Block:(StateBlock)block;
@end
